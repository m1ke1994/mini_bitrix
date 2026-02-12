import logging
from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from analytics_app.models import Event
from analytics_app.serializers import PublicEventCreateSerializer
from accounts.permissions import IsClientUser
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


class AnalyticsSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientUser]

    def get(self, request):
        client = request.client

        visit_count = Event.objects.filter(client=client, event_type=Event.EventType.VISIT).count()
        form_submit_count = Event.objects.filter(client=client, event_type=Event.EventType.FORM_SUBMIT).count()
        leads_count = Lead.objects.filter(client=client).count()
        conversion = (form_submit_count / visit_count) if visit_count else 0

        from_date = timezone.now().date() - timedelta(days=13)

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
            }
        )
