import logging
from datetime import datetime, timedelta

from django.db.models import Avg, Count, OuterRef, Q, Subquery, Sum
from django.db.models.functions import ExtractHour, ExtractWeekDay, TruncDate, TruncWeek
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsClientUser
from analytics_app.models import Event
from analytics_app.models import PageView as AnalyticsPageView
from analytics_app.serializers import PublicAnalyticsEventSerializer, PublicEventCreateSerializer
from analytics_app.services.ai_advisor import generate_ai_advisor_recommendations
from analytics_app.services.ai_recommendations import build_ai_event_signals_payload
from analytics_app.services.device_stats import get_device_distribution
from analytics_app.services.local_recommendations import build_behavior_recommendations
from analytics_app.services.metrics import default_period_days, get_metrics, period_bounds
from analytics_app.services.report_builder import build_full_report
from clients.permissions import HasValidApiKey
<<<<<<< HEAD
=======
from leads.tasks import recalculate_lead_score_for_session
from leads.models import Lead, LeadActivity, PipelineStage
>>>>>>> c49e52d863c20cba3901447a483ff75db2d8a736
from tracker.models import Visit
from tracker.services.client_scope import visit_site_client_q
from subscriptions.permissions import HasActiveSubscription

logger = logging.getLogger(__name__)

def _default_period_days(days=14):
    return default_period_days(days=days)


def _parse_date(value, fallback):
    if not value:
        return fallback
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return fallback


def _period_range(request, days=14):
    default_from, default_to = _default_period_days(days=days)
    date_from = _parse_date(request.query_params.get("date_from"), default_from)
    date_to = _parse_date(request.query_params.get("date_to"), default_to)
    if date_from > date_to:
        date_from, date_to = date_to, date_from
    from_dt, to_dt = period_bounds(date_from, date_to, timezone.get_current_timezone())
    return date_from, date_to, from_dt, to_dt


def _build_ai_event_signals_payload(client, from_dt, to_dt):
    return build_ai_event_signals_payload(client=client, from_dt=from_dt, to_dt=to_dt)


def _build_summary_payload(client, from_dt, to_dt):
    report = build_full_report(client=client, date_from=from_dt.date(), date_to=to_dt.date())
    summary = report["summary"]
    daily_stats = report["daily_stats"]
    engagement = report.get("engagement") or {}

    visits_by_day = [{"day": row["day"], "count": row["visits"]} for row in daily_stats]
    unique_by_day = [{"day": row["day"], "count": row["unique_users"]} for row in daily_stats]
    forms_by_day = [{"day": row["day"], "count": row["forms"]} for row in daily_stats]
    leads_by_day = [{"day": row["day"], "count": row["leads"]} for row in daily_stats]

    source_performance = [
        {
            "source": row["source"],
            "visits": row["visits"],
            "leads": row["leads"],
            "conversion_pct": row["conversion_pct"],
        }
        for row in report["sources"]
    ]
    top_sources = [{"source": row["source"], "count": row["visits"]} for row in report["sources"][:5]]
    ai_event_signals = _build_ai_event_signals_payload(client=client, from_dt=from_dt, to_dt=to_dt)

    payload = {
        "visit_count": summary["visits"],
        "visitors_unique": summary["unique_users"],
        "form_submit_count": summary["forms"],
        "leads_count": summary["leads"],
        "notifications_sent_count": summary.get("notifications_sent", 0),
        "conversion": summary["conversion"],
        "visits_by_day": visits_by_day,
        "unique_by_day": unique_by_day,
        "forms_by_day": forms_by_day,
        "leads_by_day": leads_by_day,
        "latest_leads": report["leads"][:10],
        "avg_time_on_site": summary.get("avg_visit_duration_seconds", 0),
        "avg_visit_duration_seconds": summary.get("avg_visit_duration_seconds", 0),
        "total_time_on_site_seconds": summary.get("total_time_on_site_seconds", 0),
        "avg_session_duration": 0,
        "avg_scroll_depth": 0,
        "total_sessions": 0,
        "avg_page_views_per_session": 0,
        "top_sources": top_sources,
        "source_performance": source_performance,
        "conversion_by_pages": report["page_conversion"],
        "top_clicks": report["top_clicks"][:10],
        "total_clicks": sum(item["count"] for item in report["top_clicks"]),
        "engagement_pages": engagement.get("pages", []),
        "ai_event_signals": ai_event_signals,
    }
    payload["recommendations"] = build_behavior_recommendations(payload)
    return payload
<<<<<<< HEAD
=======


def _leads_in_period(client, from_dt, to_dt):
    return Lead.objects.filter(client=client, created_at__gte=from_dt, created_at__lte=to_dt)


def _source_label(utm_source, utm_medium, source_url):
    if (utm_source or "").strip():
        return (utm_source or "").strip()
    if (utm_medium or "").strip():
        return f"medium:{(utm_medium or '').strip()}"
    if (source_url or "").strip():
        return (source_url or "").strip()
    return "unknown"
>>>>>>> c49e52d863c20cba3901447a483ff75db2d8a736


class PublicEventCreateView(CreateAPIView):
    serializer_class = PublicEventCreateSerializer
    permission_classes = [HasValidApiKey]
    throttle_scope = "public_event"

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["client"] = self.request.client
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            event = serializer.save()
        except Exception:
            logger.exception("Failed to create public event")
            return Response({"detail": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            recalculate_lead_score_for_session.delay(
                request.client.id,
                "",
                request.data.get("visitor_id") or "",
            )
        except Exception:
            logger.exception("Failed to enqueue lead score recalculation for public event client_id=%s", request.client.id)
        if event.event_type == Event.EventType.VISIT:
            logger.info(
                "Visit event stored: client_id=%s event_id=%s visitor_id=%s page_url=%s",
                request.client.id,
                event.id,
                event.visitor_id,
                event.page_url,
            )
        return Response({"id": event.id}, status=status.HTTP_201_CREATED)


class PublicVisitTrackView(APIView):
    permission_classes = [HasValidApiKey]
    throttle_scope = "public_event"

    def post(self, request, *args, **kwargs):
        payload = {
            "event_type": Event.EventType.VISIT,
            "page_url": request.data.get("page_url"),
            "element_id": request.data.get("element_id"),
            "visitor_id": request.data.get("visitor_id"),
        }
        serializer = PublicEventCreateSerializer(data=payload, context={"client": request.client})
        serializer.is_valid(raise_exception=True)
        try:
            event = serializer.save()
        except Exception:
            logger.exception("Failed to create visit event")
            return Response({"detail": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.info(
            "Visit track endpoint stored event: client_id=%s event_id=%s visitor_id=%s page_url=%s",
            request.client.id,
            event.id,
            event.visitor_id,
            event.page_url,
        )
        return Response({"id": event.id, "event_type": event.event_type}, status=status.HTTP_200_OK)


class PublicAnalyticsEventCreateView(CreateAPIView):
    serializer_class = PublicAnalyticsEventSerializer
    permission_classes = [HasValidApiKey]
    throttle_scope = "public_analytics_event"

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["client"] = self.request.client
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = serializer.save()
        except Exception:
            logger.exception("Failed to create analytics event")
            return Response({"detail": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            recalculate_lead_score_for_session.delay(
                request.client.id,
                request.data.get("session_id") or "",
                request.data.get("visitor_id") or "",
            )
        except Exception:
            logger.exception(
                "Failed to enqueue lead score recalculation for analytics event client_id=%s",
                request.client.id,
            )
        logger.info(
            "analytics.event stored: client_id=%s type=%s visitor_id=%s session_id=%s result=%s",
            request.client.id,
            request.data.get("event_type"),
            request.data.get("visitor_id"),
            request.data.get("session_id"),
            result,
        )
        return Response(result, status=status.HTTP_201_CREATED)


class AnalyticsSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientUser, HasActiveSubscription]

    def get(self, request):
        client = request.client
        date_from, date_to, from_dt, to_dt = _period_range(request, days=14)
        payload = _build_summary_payload(client=client, from_dt=from_dt, to_dt=to_dt)
        payload["period"] = {"date_from": date_from, "date_to": date_to}
        logger.info(
            "analytics.summary: client_id=%s from=%s to=%s visits=%s unique=%s leads=%s",
            client.id,
            date_from,
            date_to,
            payload["visit_count"],
            payload["visitors_unique"],
            payload["leads_count"],
        )
        return Response(payload)


class AnalyticsAiRecommendationsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientUser, HasActiveSubscription]

    def get(self, request):
        date_from, date_to, from_dt, to_dt = _period_range(request, days=14)
        summary_payload = _build_summary_payload(client=request.client, from_dt=from_dt, to_dt=to_dt)
        payload = summary_payload.get("recommendations") or build_behavior_recommendations(summary_payload)
<<<<<<< HEAD
=======
        conversion_by_stage = list(
            _leads_in_period(request.client, from_dt, to_dt)
            .values("stage__name")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        peak_hours_rows = (
            LeadActivity.objects.filter(
                lead__client=request.client,
                created_at__gte=from_dt,
                created_at__lte=to_dt,
            )
            .annotate(hour=ExtractHour("created_at"))
            .values("hour")
            .annotate(count=Count("id"))
            .order_by("-count")[:5]
        )
        stale_leads = Lead.objects.filter(
            client=request.client,
            stage__is_closed_stage=False,
            last_activity_at__lt=timezone.now() - timedelta(hours=24),
        ).count()
        source_perf = summary_payload.get("source_performance") or []
        top_utm = sorted(source_perf, key=lambda item: float(item.get("conversion_pct") or 0), reverse=True)[:5]
        advisor = generate_ai_advisor_recommendations(
            client_id=request.client.id,
            period_from=str(date_from),
            period_to=str(date_to),
            payload={
                "leads_by_source": source_perf,
                "conversion_by_stage": conversion_by_stage,
                "avg_response_time": summary_payload.get("avg_visit_duration_seconds", 0),
                "peak_hours": list(peak_hours_rows),
                "stale_leads": stale_leads,
                "top_converting_utm": top_utm,
            },
        )
        payload["advisor"] = advisor
>>>>>>> c49e52d863c20cba3901447a483ff75db2d8a736
        payload["period"] = {"date_from": date_from, "date_to": date_to}
        return Response(payload)


class AnalyticsOverviewView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientUser, HasActiveSubscription]

    def get(self, request):
        client = request.client
        date_from, date_to, _, _ = _period_range(request, days=14)
        metrics = get_metrics(client, date_from, date_to)
        response = {
            "period": {"date_from": date_from, "date_to": date_to},
            "visits_total": metrics["visits"],
            "visitors_unique": metrics["unique_users"],
            "forms_total": metrics["forms"],
            "leads_total": metrics["leads"],
            "notifications_sent_total": metrics["notifications_sent"],
            "conversion": metrics["conversion"],
            "total_time_on_site_seconds": metrics["total_time_on_site_seconds"],
            "avg_visit_duration_seconds": metrics["avg_visit_duration_seconds"],
        }
        logger.info(
            "analytics.overview: client_id=%s from=%s to=%s payload=%s",
            client.id,
            date_from,
            date_to,
            response,
        )
        return Response(response)


class AnalyticsEngagementView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientUser, HasActiveSubscription]

    def get(self, request):
        client = request.client
        date_from, date_to, _, _ = _period_range(request, days=14)
        report = build_full_report(client=client, date_from=date_from, date_to=date_to)
        engagement = report.get("engagement") or {}
        response = {
            "period": {"date_from": date_from, "date_to": date_to},
            "avg_time_on_page_seconds": engagement.get("avg_visit_duration_seconds", 0),
            "total_time_on_site_seconds": engagement.get("total_time_on_site_seconds", 0),
            "pages": engagement.get("pages", []),
        }
        logger.info(
            "analytics.engagement: client_id=%s from=%s to=%s total_time=%s pages=%s",
            client.id,
            date_from,
            date_to,
            response["total_time_on_site_seconds"],
            len(response["pages"]),
        )
        return Response(response)


class AnalyticsUniqueDailyView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientUser, HasActiveSubscription]

    def get(self, request):
        client = request.client
        date_from, date_to, from_dt, to_dt = _period_range(request, days=14)
        unique_filter = Q(visitor_id__isnull=False) & ~Q(visitor_id="")
        visits_qs = Visit.objects.filter(
            visit_site_client_q(client),
            started_at__gte=from_dt,
            started_at__lte=to_dt,
            is_bot=False,
        )
        rows_with_id = list(
            visits_qs.filter(unique_filter)
            .annotate(day=TruncDate("started_at"))
            .values("day")
            .annotate(count=Count("visitor_id", distinct=True))
            .order_by("day")
        )
        rows_without_id = list(
            visits_qs.exclude(unique_filter)
            .annotate(day=TruncDate("started_at"))
            .values("day")
            .annotate(count=Count("session_id", distinct=True))
            .order_by("day")
        )
        merged_rows = {}
        for row in rows_with_id + rows_without_id:
            day = row.get("day")
            merged_rows[day] = merged_rows.get(day, 0) + int(row.get("count") or 0)
        rows = [{"day": day, "count": count} for day, count in sorted(merged_rows.items())]

        metrics = get_metrics(client, date_from, date_to)
        total_unique = metrics["unique_users"]
        logger.info(
            "analytics.unique_daily: client_id=%s from=%s to=%s total_unique=%s days=%s",
            client.id,
            date_from,
            date_to,
            total_unique,
            len(rows),
        )
        return Response(
            {
                "period": {"date_from": date_from, "date_to": date_to},
                "total_unique": total_unique,
                "daily": rows,
            }
        )


class AnalyticsDevicesView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientUser, HasActiveSubscription]

    def get(self, request):
        client = request.client
        date_from, date_to, _, _ = _period_range(request, days=14)
        payload = get_device_distribution(client=client, date_from=date_from, date_to=date_to)
        response = {
            "period": {"date_from": date_from, "date_to": date_to},
            "devices": payload["devices"],
            "browsers": payload["browsers"],
            "os": payload["os"],
        }
        logger.info(
            "analytics.devices: client_id=%s from=%s to=%s payload=%s",
            client.id,
            date_from,
            date_to,
            response,
        )
        return Response(response)


class AnalyticsFunnelView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientUser, HasActiveSubscription]

    def get(self, request):
        client = request.client
        date_from, date_to, from_dt, to_dt = _period_range(request, days=30)
        leads_qs = _leads_in_period(client, from_dt, to_dt)

        stage_ids = leads_qs.values_list("stage_id", flat=True)
        stage_qs = (
            PipelineStage.objects.filter(pipeline__client=client, id__in=stage_ids)
            .annotate(
                leads_count=Count("leads", filter=Q(leads__created_at__gte=from_dt, leads__created_at__lte=to_dt)),
                estimated_value_total=Sum(
                    "leads__estimated_value",
                    filter=Q(leads__created_at__gte=from_dt, leads__created_at__lte=to_dt),
                ),
            )
            .order_by("pipeline_id", "order", "id")
        )

        stages = []
        prev_count = None
        total_leads = leads_qs.count()
        for stage in stage_qs:
            count = int(stage.leads_count or 0)
            if prev_count and prev_count > 0:
                conversion_from_prev = round((count / prev_count) * 100.0, 2)
            else:
                conversion_from_prev = 100.0
            conversion_from_first = round((count / total_leads) * 100.0, 2) if total_leads else 0.0
            stages.append(
                {
                    "stage_id": stage.id,
                    "stage": stage.name,
                    "order": stage.order,
                    "count": count,
                    "conversion_from_previous_pct": conversion_from_prev,
                    "conversion_from_first_pct": conversion_from_first,
                    "estimated_value_total": float(stage.estimated_value_total or 0),
                }
            )
            prev_count = count

        return Response(
            {
                "period": {"date_from": date_from, "date_to": date_to},
                "total_leads": total_leads,
                "stages": stages,
            }
        )


class AnalyticsSourcesView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientUser, HasActiveSubscription]

    def get(self, request):
        client = request.client
        date_from, date_to, from_dt, to_dt = _period_range(request, days=30)
        leads_rows = list(
            _leads_in_period(client, from_dt, to_dt)
            .values("utm_source", "utm_medium", "source_url")
            .annotate(
                leads_count=Count("id"),
                deals_count=Count("id", filter=Q(stage__is_closed_stage=True) | Q(status=Lead.Status.CLOSED)),
                avg_score=Avg("score"),
            )
            .order_by("-leads_count", "utm_source", "utm_medium")
        )
        items = []
        for row in leads_rows:
            leads_count = int(row["leads_count"] or 0)
            deals_count = int(row["deals_count"] or 0)
            conversion = round((deals_count / leads_count) * 100.0, 2) if leads_count else 0.0
            items.append(
                {
                    "source": _source_label(row.get("utm_source"), row.get("utm_medium"), row.get("source_url")),
                    "utm_source": row.get("utm_source"),
                    "utm_medium": row.get("utm_medium"),
                    "source_url": row.get("source_url"),
                    "leads": leads_count,
                    "deals": deals_count,
                    "conversion_pct": conversion,
                    "avg_score": round(float(row.get("avg_score") or 0.0), 2),
                }
            )

        referrers = list(
            AnalyticsPageView.objects.filter(client=client, created_at__gte=from_dt, created_at__lte=to_dt)
            .exclude(referrer__isnull=True)
            .exclude(referrer="")
            .values("referrer")
            .annotate(visits=Count("id"))
            .order_by("-visits")[:10]
        )

        return Response(
            {
                "period": {"date_from": date_from, "date_to": date_to},
                "items": items,
                "top_referrers": referrers,
            }
        )


class AnalyticsTimelineView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientUser, HasActiveSubscription]

    def get(self, request):
        client = request.client
        granularity = (request.query_params.get("granularity") or "day").strip().lower()
        date_from, date_to, from_dt, to_dt = _period_range(request, days=30)
        leads_qs = _leads_in_period(client, from_dt, to_dt)

        trunc_fn = TruncWeek if granularity == "week" else TruncDate
        rows = (
            leads_qs.annotate(period=trunc_fn("created_at"))
            .values("period")
            .annotate(
                leads_count=Count("id"),
                deals_count=Count("id", filter=Q(stage__is_closed_stage=True) | Q(status=Lead.Status.CLOSED)),
            )
            .order_by("period")
        )
        timeline = [
            {
                "period": row["period"].date().isoformat() if hasattr(row["period"], "date") else str(row["period"]),
                "leads_count": int(row["leads_count"] or 0),
                "deals_count": int(row["deals_count"] or 0),
            }
            for row in rows
        ]
        return Response(
            {
                "period": {"date_from": date_from, "date_to": date_to},
                "granularity": "week" if granularity == "week" else "day",
                "items": timeline,
            }
        )


class AnalyticsResponseTimeView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientUser, HasActiveSubscription]

    def get(self, request):
        client = request.client
        date_from, date_to, from_dt, to_dt = _period_range(request, days=30)
        first_activity_subquery = Subquery(
            LeadActivity.objects.filter(lead_id=OuterRef("pk"))
            .exclude(action_type=LeadActivity.ActionType.CREATED)
            .order_by("created_at")
            .values("created_at")[:1]
        )
        rows = list(
            _leads_in_period(client, from_dt, to_dt)
            .annotate(first_activity_at=first_activity_subquery)
            .values("id", "created_at", "first_activity_at")
        )
        response_seconds = []
        for row in rows:
            first = row.get("first_activity_at")
            created = row.get("created_at")
            if not first or not created:
                continue
            diff = (first - created).total_seconds()
            if diff >= 0:
                response_seconds.append(diff)

        avg_seconds = round(sum(response_seconds) / len(response_seconds), 2) if response_seconds else 0.0
        return Response(
            {
                "period": {"date_from": date_from, "date_to": date_to},
                "avg_first_response_seconds": avg_seconds,
                "avg_first_response_hours": round(avg_seconds / 3600.0, 2) if avg_seconds else 0.0,
                "leads_with_response": len(response_seconds),
                "leads_without_response": len(rows) - len(response_seconds),
            }
        )


class AnalyticsConversionRateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientUser, HasActiveSubscription]

    def get(self, request):
        client = request.client
        date_from, date_to, from_dt, to_dt = _period_range(request, days=30)
        rows = list(
            _leads_in_period(client, from_dt, to_dt)
            .values("utm_source", "utm_medium")
            .annotate(
                leads=Count("id"),
                deals=Count("id", filter=Q(stage__is_closed_stage=True) | Q(status=Lead.Status.CLOSED)),
            )
            .order_by("-leads")
        )

        items = []
        for row in rows:
            leads_count = int(row["leads"] or 0)
            deals_count = int(row["deals"] or 0)
            conversion = round((deals_count / leads_count) * 100.0, 2) if leads_count else 0.0
            items.append(
                {
                    "channel": _source_label(row.get("utm_source"), row.get("utm_medium"), None),
                    "utm_source": row.get("utm_source"),
                    "utm_medium": row.get("utm_medium"),
                    "leads": leads_count,
                    "deals": deals_count,
                    "conversion_pct": conversion,
                }
            )
        return Response(
            {
                "period": {"date_from": date_from, "date_to": date_to},
                "items": items,
            }
        )


class AnalyticsHeatmapView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientUser, HasActiveSubscription]

    def get(self, request):
        client = request.client
        date_from, date_to, from_dt, to_dt = _period_range(request, days=30)
        rows = (
            LeadActivity.objects.filter(lead__client=client, created_at__gte=from_dt, created_at__lte=to_dt)
            .annotate(hour=ExtractHour("created_at"), weekday=ExtractWeekDay("created_at"))
            .values("hour", "weekday")
            .annotate(count=Count("id"))
            .order_by("weekday", "hour")
        )
        items = [
            {
                "weekday": int(row["weekday"] or 0),
                "hour": int(row["hour"] or 0),
                "count": int(row["count"] or 0),
            }
            for row in rows
        ]
        return Response(
            {
                "period": {"date_from": date_from, "date_to": date_to},
                "items": items,
            }
        )


class AnalyticsAiAdvisorView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientUser, HasActiveSubscription]

    def get(self, request):
        client = request.client
        date_from, date_to, from_dt, to_dt = _period_range(request, days=30)
        summary_payload = _build_summary_payload(client=client, from_dt=from_dt, to_dt=to_dt)
        leads_by_source = summary_payload.get("source_performance") or []
        conversion_by_stage = list(
            _leads_in_period(client, from_dt, to_dt)
            .values("stage__name")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        response_time_payload = AnalyticsResponseTimeView().get(request).data
        peak_hours_rows = (
            LeadActivity.objects.filter(lead__client=client, created_at__gte=from_dt, created_at__lte=to_dt)
            .annotate(hour=ExtractHour("created_at"))
            .values("hour")
            .annotate(count=Count("id"))
            .order_by("-count")[:5]
        )
        stale_leads = Lead.objects.filter(
            client=client,
            stage__is_closed_stage=False,
            last_activity_at__lt=timezone.now() - timedelta(hours=24),
        ).count()
        top_utm = sorted(leads_by_source, key=lambda item: float(item.get("conversion_pct") or 0), reverse=True)[:5]

        advisor_payload = generate_ai_advisor_recommendations(
            client_id=client.id,
            period_from=str(date_from),
            period_to=str(date_to),
            payload={
                "leads_by_source": leads_by_source,
                "conversion_by_stage": conversion_by_stage,
                "avg_response_time": response_time_payload.get("avg_first_response_seconds", 0),
                "peak_hours": list(peak_hours_rows),
                "stale_leads": stale_leads,
                "top_converting_utm": top_utm,
            },
        )
        advisor_payload["period"] = {"date_from": date_from, "date_to": date_to}
        return Response(advisor_payload)
