from __future__ import annotations

from dataclasses import dataclass

from analytics_app.models import Event as AnalyticsEvent
from analytics_app.models import PageView as AnalyticsPageView
from leads.crm import log_lead_activity
from leads.models import Lead, LeadActivity
from tracker.models import Event as TrackerEvent
from tracker.models import Visit
from tracker.services.client_scope import tracker_event_site_client_q, visit_site_client_q


@dataclass
class LeadScoringSignals:
    visits_count: int = 0
    page_views_count: int = 0
    form_interactions_count: int = 0


class LeadScoringService:
    RULE_POINTS = {
        "has_phone": 15,
        "has_email": 12,
        "has_message": 8,
        "utm_paid": 20,
        "repeat_visits": 15,
        "page_views": 10,
        "form_interactions": 20,
    }
    MAX_SCORE = 100

    @classmethod
    def collect_signals(cls, lead: Lead, *, session_id: str = "", visitor_id: str = "") -> LeadScoringSignals:
        sid = (session_id or lead.session_id or "").strip()
        vid = (visitor_id or lead.visitor_id or "").strip()

        visits_qs = Visit.objects.filter(visit_site_client_q(lead.client), is_bot=False)
        if sid:
            visits_qs = visits_qs.filter(session_id=sid)
        elif vid:
            visits_qs = visits_qs.filter(visitor_id=vid)
        else:
            visits_qs = visits_qs.none()
        visits_count = visits_qs.count()

        page_views_qs = AnalyticsPageView.objects.filter(client=lead.client)
        if sid:
            page_views_qs = page_views_qs.filter(session_id=sid)
        elif vid:
            page_views_qs = page_views_qs.filter(visitor_id=vid)
        else:
            page_views_qs = page_views_qs.none()
        page_views_count = page_views_qs.count()

        form_qs = AnalyticsEvent.objects.filter(client=lead.client, event_type=AnalyticsEvent.EventType.FORM_SUBMIT)
        if sid:
            form_qs = form_qs.filter(page_url__isnull=False).filter(
                client__page_views__session_id=sid
            ).distinct()
        elif vid:
            form_qs = form_qs.filter(visitor_id=vid)
        else:
            form_qs = form_qs.none()
        form_interactions_count = form_qs.count()

        if sid and form_interactions_count == 0:
            form_interactions_count = TrackerEvent.objects.filter(
                tracker_event_site_client_q(lead.client),
                visit__session_id=sid,
                type="form_submit",
            ).count()

        return LeadScoringSignals(
            visits_count=visits_count,
            page_views_count=page_views_count,
            form_interactions_count=form_interactions_count,
        )

    @classmethod
    def calculate(cls, lead: Lead, *, signals: LeadScoringSignals | None = None) -> int:
        signals = signals or LeadScoringSignals()
        score = 0

        if (lead.phone or "").strip():
            score += cls.RULE_POINTS["has_phone"]
        if (lead.email or "").strip():
            score += cls.RULE_POINTS["has_email"]
        if (lead.message or "").strip():
            score += cls.RULE_POINTS["has_message"]
        if (lead.utm_medium or "").strip().lower() in {"paid", "cpc", "ppc"}:
            score += cls.RULE_POINTS["utm_paid"]
        if signals.visits_count > 1:
            score += cls.RULE_POINTS["repeat_visits"]
        if signals.page_views_count >= 3:
            score += cls.RULE_POINTS["page_views"]
        if signals.form_interactions_count > 0:
            score += cls.RULE_POINTS["form_interactions"]

        return min(score, cls.MAX_SCORE)

    @classmethod
    def apply(
        cls,
        lead: Lead,
        *,
        session_id: str = "",
        visitor_id: str = "",
        log_reason: str = "auto",
    ) -> int:
        signals = cls.collect_signals(lead, session_id=session_id, visitor_id=visitor_id)
        next_score = cls.calculate(lead, signals=signals)
        if next_score == int(lead.score or 0):
            return next_score

        old_score = int(lead.score or 0)
        lead.score = next_score
        lead.save(update_fields=["score", "updated_at"])
        log_lead_activity(
            lead,
            action_type=LeadActivity.ActionType.SCORE_UPDATED,
            description=f"Скоринг обновлен: {old_score} -> {next_score}",
            metadata={
                "reason": log_reason,
                "signals": {
                    "visits_count": signals.visits_count,
                    "page_views_count": signals.page_views_count,
                    "form_interactions_count": signals.form_interactions_count,
                },
            },
        )
        return next_score

    @classmethod
    def recalculate_for_queryset(cls, queryset):
        updated = 0
        for lead in queryset.iterator():
            before = int(lead.score or 0)
            after = cls.apply(lead, session_id=lead.session_id, visitor_id=lead.visitor_id, log_reason="bulk_recalculate")
            if before != after:
                updated += 1
        return updated
