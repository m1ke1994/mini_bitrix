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
        return Response({"id": event.id}, status=status.HTTP_201_CREATED)


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
        from_date = timezone.now().date() - timedelta(days=13)

        visit_count = Event.objects.filter(client=client, event_type=Event.EventType.VISIT).count()
        form_submit_count = Event.objects.filter(client=client, event_type=Event.EventType.FORM_SUBMIT).count()
        leads_count = Lead.objects.filter(client=client).count()
        conversion = (form_submit_count / visit_count) if visit_count else 0

        visits_by_day = (
            Event.objects.filter(
                client=client,
                event_type=Event.EventType.VISIT,
                created_at__date__gte=from_date,
            )
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )
        forms_by_day = (
            Event.objects.filter(
                client=client,
                event_type=Event.EventType.FORM_SUBMIT,
                created_at__date__gte=from_date,
            )
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )
        leads_by_day = (
            Lead.objects.filter(client=client, created_at__date__gte=from_date)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )
        latest_leads = Lead.objects.filter(client=client).order_by("-created_at")[:10]

        page_view_qs = PageView.objects.filter(client=client, created_at__date__gte=from_date)
        avg_time_on_site = page_view_qs.aggregate(v=Avg("duration_seconds"))["v"] or 0
        avg_scroll_depth = page_view_qs.aggregate(v=Avg("max_scroll_depth"))["v"] or 0
        avg_session_duration = (
            page_view_qs.values("session_id")
            .annotate(total_duration=Sum("duration_seconds"))
            .aggregate(v=Avg("total_duration"))["v"]
            or 0
        )

        source_counter = {}
        for item in page_view_qs.values("utm_source", "referrer"):
            source = (item.get("utm_source") or "").strip()
            if not source:
                referrer = (item.get("referrer") or "").strip()
                if referrer:
                    source = urlparse(referrer).netloc or "referral"
                else:
                    source = "direct"
            source_counter[source] = source_counter.get(source, 0) + 1
        formatted_sources = [
            {"source": source, "count": count}
            for source, count in sorted(source_counter.items(), key=lambda x: x[1], reverse=True)[:5]
        ]

        conversion_by_pages_qs = (
            page_view_qs.values("pathname")
            .annotate(
                visits=Count("id"),
                leads=Sum("attributed_leads"),
            )
            .order_by("-visits")[:20]
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
            ClickEvent.objects.filter(client=client, created_at__date__gte=from_date)
            .values("page_pathname", "element_text", "element_id", "element_class")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )
        top_clicks = list(top_clicks_qs)

        return Response(
            {
                "visit_count": visit_count,
                "form_submit_count": form_submit_count,
                "leads_count": leads_count,
                "conversion": round(conversion, 4),
                "visits_by_day": list(visits_by_day),
                "forms_by_day": list(forms_by_day),
                "leads_by_day": list(leads_by_day),
                "latest_leads": LeadSerializer(latest_leads, many=True).data,
                "avg_time_on_site": round(float(avg_time_on_site), 2),
                "avg_session_duration": round(float(avg_session_duration), 2),
                "avg_scroll_depth": round(float(avg_scroll_depth), 2),
                "top_sources": formatted_sources,
                "conversion_by_pages": conversion_by_pages,
                "top_clicks": top_clicks,
            }
        )
