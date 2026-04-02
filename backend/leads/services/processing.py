from __future__ import annotations

from dataclasses import dataclass

from analytics_app.models import PageView
from django.db import models
from leads.crm import get_default_stage, log_lead_activity
from leads.models import Lead, LeadActivity, WidgetVariant
from leads.realtime import broadcast_lead_event
from leads.services.dedup import MergeLeadDeduplicationStrategy
from leads.services.lead_scoring import LeadScoringService
from leads.services.notifications import serialize_lead


@dataclass
class LeadProcessResult:
    lead: Lead
    created: bool
    merged: bool


def process_public_lead_submission(
    *,
    client,
    payload: dict,
    session_id: str = "",
    visitor_id: str = "",
    variant_id: int | None = None,
    dedup_strategy=None,
) -> LeadProcessResult:
    normalized_payload = dict(payload or {})
    normalized_payload["session_id"] = (session_id or normalized_payload.get("session_id") or "").strip()
    normalized_payload["visitor_id"] = (visitor_id or normalized_payload.get("visitor_id") or "").strip()

    strategy = dedup_strategy or MergeLeadDeduplicationStrategy()
    default_stage = get_default_stage(client)

    def create_new_lead(data: dict) -> Lead:
        lead = Lead.objects.create(
            client=client,
            stage=default_stage,
            status=Lead.Status.NEW,
            name=data.get("name") or "",
            phone=data.get("phone") or None,
            normalized_phone=data.get("normalized_phone") or "",
            email=data.get("email") or None,
            normalized_email=data.get("normalized_email") or "",
            message=data.get("message") or None,
            source_url=data.get("source_url") or None,
            utm_source=data.get("utm_source") or None,
            utm_medium=data.get("utm_medium") or None,
            utm_campaign=data.get("utm_campaign") or None,
            session_id=data.get("session_id") or "",
            visitor_id=data.get("visitor_id") or "",
        )
        log_lead_activity(
            lead,
            action_type=LeadActivity.ActionType.CREATED,
            description="Лид создан из публичной формы",
            metadata={
                "source": "public_api",
                "session_id": data.get("session_id") or None,
                "visitor_id": data.get("visitor_id") or None,
                "variant_id": variant_id,
            },
        )
        return lead

    dedup_result = strategy.upsert(
        client=client,
        payload=normalized_payload,
        create_lead_fn=create_new_lead,
    )

    lead = dedup_result.lead

    if normalized_payload["session_id"]:
        latest_page_view = (
            PageView.objects.filter(client=client, session_id=normalized_payload["session_id"])
            .order_by("-created_at")
            .first()
        )
        if latest_page_view:
            latest_page_view.attributed_leads += 1
            latest_page_view.save(update_fields=["attributed_leads", "updated_at"])

    LeadScoringService.apply(
        lead,
        session_id=lead.session_id or normalized_payload["session_id"],
        visitor_id=lead.visitor_id or normalized_payload["visitor_id"],
        log_reason="created" if dedup_result.created else "merged",
    )

    if variant_id:
        WidgetVariant.objects.filter(
            id=variant_id,
            client_id=client.id,
            is_active=True,
        ).update(conversions=models.F("conversions") + 1)

    from leads.tasks import auto_respond_lead, notify_new_lead  # local import to avoid circular dependency

    notify_new_lead.delay(lead.id)
    auto_respond_lead.delay(lead.id)
    broadcast_lead_event(
        client_id=client.id,
        event="lead_created" if dedup_result.created else "lead_updated",
        payload=serialize_lead(lead),
    )

    return LeadProcessResult(lead=lead, created=dedup_result.created, merged=dedup_result.merged)
