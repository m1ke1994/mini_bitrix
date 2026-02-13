import logging
from datetime import timedelta
from urllib.parse import urlparse

from django.db.models import Avg, Count, Sum
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
                "Visit event stored: client_id=%s event_id=%s page_url=%s",
                request.client.id,
                event.id,
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
        }
        serializer = PublicEventCreateSerializer(data=payload, context={"client": request.client})
        serializer.is_valid(raise_exception=True)
        try:
            event = serializer.save()
        except Exception:
            logger.exception("Failed to create visit event")
            return Response({"detail": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.info(
            "Visit track endpoint stored event: client_id=%s event_id=%s page_url=%s",
            request.client.id,
            event.id,
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
        return Response(result, status=status.HTTP_201_CREATED)


class AnalyticsSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientUser]

    def get(self, request):
        client = request.client
        from_dt = timezone.now() - timedelta(days=13)

        # Exclude technical fetch-interceptor marker to avoid double counting
        # a single real form submission as two "form_submit" events.
        form_submit_count = (
            Event.objects.filter(client=client, event_type=Event.EventType.FORM_SUBMIT)
            .exclude(element_id="fetch_json")
            .count()
        )
        leads_count = Lead.objects.filter(client=client).count()

        visits_by_day = (
            Event.objects.filter(
                client=client,
                event_type=Event.EventType.VISIT,
                created_at__gte=from_dt,
            )
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )
        visits_by_day_list = list(visits_by_day)
        forms_by_day = (
            Event.objects.filter(
                client=client,
                event_type=Event.EventType.FORM_SUBMIT,
                created_at__gte=from_dt,
            )
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )
        leads_by_day = (
            Lead.objects.filter(client=client, created_at__gte=from_dt)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )
        latest_leads = Lead.objects.filter(client=client).order_by("-created_at")[:10]

        page_view_qs = PageView.objects.filter(client=client, created_at__gte=from_dt)
        # Keep "Overview -> Visits" consistent with "Top sources" data source/filtering.
        visit_count = page_view_qs.count()
        conversion = (form_submit_count / visit_count) if visit_count else 0
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
            ClickEvent.objects.filter(client=client, created_at__gte=from_dt)
            .values("page_pathname", "element_text", "element_id", "element_class")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )
        total_clicks = ClickEvent.objects.filter(client=client, created_at__gte=from_dt).count()
        top_clicks = []
        for item in top_clicks_qs:
            row = dict(item)
            row["percent_of_total"] = round((row["count"] / total_clicks) * 100, 2) if total_clicks else 0
            top_clicks.append(row)

        logger.info(
            "Analytics summary: client_id=%s visits_total=%s forms_total=%s leads_total=%s visit_days=%s",
            client.id,
            visit_count,
            form_submit_count,
            leads_count,
            len(visits_by_day_list),
        )

        return Response(
            {
                "visit_count": visit_count,
                "form_submit_count": form_submit_count,
                "leads_count": leads_count,
                "conversion": round(conversion, 4),
                "visits_by_day": visits_by_day_list,
                "forms_by_day": list(forms_by_day),
                "leads_by_day": list(leads_by_day),
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
        )
