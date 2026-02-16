import logging
from datetime import datetime, time, timedelta
from urllib.parse import urlparse

from django.db.models import Avg, Count, Q, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsClientUser
from analytics_app.models import ClickEvent, Event, PageView
from analytics_app.serializers import PublicAnalyticsEventSerializer, PublicEventCreateSerializer
from clients.permissions import HasValidApiKey
from leads.models import Lead
from leads.serializers import LeadSerializer

logger = logging.getLogger(__name__)


def _default_period_days(days=14):
    now = timezone.localtime()
    date_to = now.date()
    date_from = date_to - timedelta(days=days - 1)
    return date_from, date_to


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
    tz = timezone.get_current_timezone()
    from_dt = timezone.make_aware(datetime.combine(date_from, time.min), tz)
    to_dt = timezone.make_aware(datetime.combine(date_to, time.max), tz)
    return date_from, date_to, from_dt, to_dt


def _build_summary_payload(client, from_dt, to_dt):
    page_view_qs = PageView.objects.filter(client=client, created_at__gte=from_dt, created_at__lte=to_dt)
    event_qs = Event.objects.filter(client=client, created_at__gte=from_dt, created_at__lte=to_dt)
    leads_qs = Lead.objects.filter(client=client, created_at__gte=from_dt, created_at__lte=to_dt)

    form_submit_count = event_qs.filter(event_type=Event.EventType.FORM_SUBMIT).exclude(element_id="fetch_json").count()
    leads_count = leads_qs.count()
    visit_count = page_view_qs.count()

    unique_filter = Q(visitor_id__isnull=False) & ~Q(visitor_id="")
    visitors_unique = page_view_qs.filter(unique_filter).values("visitor_id").distinct().count()

    visits_by_day_list = list(
        event_qs.filter(event_type=Event.EventType.VISIT)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )
    forms_by_day = list(
        event_qs.filter(event_type=Event.EventType.FORM_SUBMIT)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )
    leads_by_day = list(
        leads_qs.annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )
    unique_by_day = list(
        page_view_qs.filter(unique_filter)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(count=Count("visitor_id", distinct=True))
        .order_by("day")
    )

    latest_leads = Lead.objects.filter(client=client).order_by("-created_at")[:10]
    conversion = (leads_count / visit_count) if visit_count else 0
    avg_time_on_site = page_view_qs.aggregate(v=Avg("duration_seconds"))["v"] or 0
    avg_scroll_depth = page_view_qs.aggregate(v=Avg("max_scroll_depth"))["v"] or 0
    total_sessions = page_view_qs.values("session_id").distinct().count()
    total_page_views = page_view_qs.count()
    avg_page_views_per_session = (total_page_views / total_sessions) if total_sessions else 0
    avg_session_duration = (
        page_view_qs.values("session_id")
        .annotate(total_duration=Sum("duration_seconds"))
        .aggregate(v=Avg("total_duration"))["v"]
        or 0
    )

    source_stats = {}
    for item in page_view_qs.values("utm_source", "referrer", "attributed_leads"):
        source = (item.get("utm_source") or "").strip().lower()
        if not source:
            referrer = (item.get("referrer") or "").strip()
            if referrer:
                source = (urlparse(referrer).netloc or "referral").lower()
            else:
                source = "direct"
        if source not in source_stats:
            source_stats[source] = {"source": source, "visits": 0, "leads": 0}
        source_stats[source]["visits"] += 1
        source_stats[source]["leads"] += int(item.get("attributed_leads") or 0)

    source_performance = []
    for stats_item in source_stats.values():
        visits = stats_item["visits"]
        leads = stats_item["leads"]
        source_performance.append(
            {
                "source": stats_item["source"],
                "visits": visits,
                "leads": leads,
                "conversion_pct": round((leads / visits) * 100, 2) if visits else 0,
            }
        )
    source_performance.sort(key=lambda item: item["visits"], reverse=True)
    formatted_sources = [{"source": item["source"], "count": item["visits"]} for item in source_performance[:5]]

    conversion_by_pages_qs = (
        page_view_qs.values("pathname")
        .annotate(
            visits=Count("id"),
            leads=Sum("attributed_leads"),
        )
        .order_by("-leads", "-visits")[:20]
    )
    conversion_by_pages = []
    for item in conversion_by_pages_qs:
        visits = item["visits"] or 0
        leads = item["leads"] or 0
        conversion_pct = round((leads / visits) * 100, 2) if visits else 0
        conversion_by_pages.append(
            {
                "pathname": item["pathname"] or "/",
                "visits": visits,
                "leads": leads,
                "conversion_pct": conversion_pct,
            }
        )

    top_clicks_qs = (
        ClickEvent.objects.filter(client=client, created_at__gte=from_dt, created_at__lte=to_dt)
        .values("page_pathname", "element_text", "element_id", "element_class")
        .annotate(count=Count("id"))
        .order_by("-count")[:10]
    )
    total_clicks = ClickEvent.objects.filter(client=client, created_at__gte=from_dt, created_at__lte=to_dt).count()
    top_clicks = []
    for item in top_clicks_qs:
        row = dict(item)
        row["percent_of_total"] = round((row["count"] / total_clicks) * 100, 2) if total_clicks else 0
        top_clicks.append(row)

    return {
        "visit_count": visit_count,
        "visitors_unique": visitors_unique,
        "form_submit_count": form_submit_count,
        "leads_count": leads_count,
        "conversion": round(conversion, 4),
        "visits_by_day": visits_by_day_list,
        "unique_by_day": unique_by_day,
        "forms_by_day": forms_by_day,
        "leads_by_day": leads_by_day,
        "latest_leads": LeadSerializer(latest_leads, many=True).data,
        "avg_time_on_site": round(float(avg_time_on_site), 2),
        "avg_session_duration": round(float(avg_session_duration), 2),
        "avg_scroll_depth": round(float(avg_scroll_depth), 2),
        "total_sessions": total_sessions,
        "avg_page_views_per_session": round(float(avg_page_views_per_session), 2),
        "top_sources": formatted_sources,
        "source_performance": source_performance,
        "conversion_by_pages": conversion_by_pages,
        "top_clicks": top_clicks,
        "total_clicks": total_clicks,
    }


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
    permission_classes = [permissions.IsAuthenticated, IsClientUser]

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


class AnalyticsOverviewView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientUser]

    def get(self, request):
        client = request.client
        date_from, date_to, from_dt, to_dt = _period_range(request, days=14)
        payload = _build_summary_payload(client=client, from_dt=from_dt, to_dt=to_dt)
        response = {
            "period": {"date_from": date_from, "date_to": date_to},
            "visits_total": payload["visit_count"],
            "visitors_unique": payload["visitors_unique"],
            "forms_total": payload["form_submit_count"],
            "leads_total": payload["leads_count"],
            "conversion": payload["conversion"],
        }
        logger.info(
            "analytics.overview: client_id=%s from=%s to=%s payload=%s",
            client.id,
            date_from,
            date_to,
            response,
        )
        return Response(response)


class AnalyticsUniqueDailyView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientUser]

    def get(self, request):
        client = request.client
        date_from, date_to, from_dt, to_dt = _period_range(request, days=14)
        unique_filter = Q(visitor_id__isnull=False) & ~Q(visitor_id="")
        rows = list(
            PageView.objects.filter(client=client, created_at__gte=from_dt, created_at__lte=to_dt)
            .filter(unique_filter)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(count=Count("visitor_id", distinct=True))
            .order_by("day")
        )
        total_unique = (
            PageView.objects.filter(client=client, created_at__gte=from_dt, created_at__lte=to_dt)
            .filter(unique_filter)
            .values("visitor_id")
            .distinct()
            .count()
        )
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
