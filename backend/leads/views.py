import logging
from hashlib import sha256

from django.db.models import Count, F
from django.utils.dateparse import parse_date
from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsClientUser
from clients.permissions import HasValidApiKey
from leads.crm import add_lead_note, ensure_default_pipeline, move_lead_to_stage, schedule_lead_contact
from leads.models import Lead, LeadActivity, Pipeline, PipelineStage, WidgetVariant
from leads.realtime import broadcast_lead_event
from leads.serializers import (
    LeadActivitySerializer,
    LeadMoveSerializer,
    LeadNoteSerializer,
    LeadScheduleSerializer,
    LeadSerializer,
    LeadStatusSerializer,
    PipelineSerializer,
    PublicLeadCreateSerializer,
    WidgetVariantImpressionSerializer,
    WidgetVariantSerializer,
)
from subscriptions.permissions import HasActiveSubscription

logger = logging.getLogger(__name__)


class PublicLeadCreateView(CreateAPIView):
    serializer_class = PublicLeadCreateSerializer
    permission_classes = [HasValidApiKey]
    throttle_scope = "public_lead"

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["client"] = self.request.client
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            lead = serializer.save()
        except Exception:
            logger.exception("Failed to create public lead")
            return Response({"detail": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"id": lead.id, "status": lead.status, "stage_id": lead.stage_id}, status=status.HTTP_201_CREATED)


class PipelineListView(ListAPIView):
    serializer_class = PipelineSerializer
    permission_classes = [permissions.IsAuthenticated, IsClientUser, HasActiveSubscription]

    def get_queryset(self):
        ensure_default_pipeline(self.request.client)
        return (
            Pipeline.objects.filter(client=self.request.client)
            .prefetch_related(
                "stages",
            )
            .order_by("-is_default", "name")
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        stage_counts = dict(
            PipelineStage.objects.filter(pipeline__client=request.client)
            .annotate(leads_count=Count("leads"))
            .values_list("id", "leads_count")
        )
        for pipeline in queryset:
            for stage in pipeline.stages.all():
                stage.leads_count = stage_counts.get(stage.id, 0)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class LeadViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = LeadSerializer
    permission_classes = [permissions.IsAuthenticated, IsClientUser, HasActiveSubscription]
    ordering_fields = ("created_at", "score", "next_contact_at")

    def get_queryset(self):
        ensure_default_pipeline(self.request.client)
        queryset = (
            Lead.objects.filter(client=self.request.client)
            .select_related("stage", "assigned_to")
            .prefetch_related("tags")
        )
        status_value = self.request.query_params.get("status")
        if status_value:
            queryset = queryset.filter(status=status_value)

        stage_id = self.request.query_params.get("stage_id")
        if stage_id and stage_id.isdigit():
            queryset = queryset.filter(stage_id=int(stage_id))

        assigned_to = self.request.query_params.get("assigned_to")
        if assigned_to and assigned_to.isdigit():
            queryset = queryset.filter(assigned_to_id=int(assigned_to))

        score_min = self.request.query_params.get("score_min")
        if score_min and score_min.isdigit():
            queryset = queryset.filter(score__gte=int(score_min))

        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        if date_from and parse_date(date_from):
            queryset = queryset.filter(created_at__date__gte=parse_date(date_from))
        if date_to and parse_date(date_to):
            queryset = queryset.filter(created_at__date__lte=parse_date(date_to))
        return queryset

    @action(detail=True, methods=["patch"], url_path="status")
    def update_status(self, request, pk=None):
        lead = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = LeadStatusSerializer(instance=lead, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        lead.refresh_from_db()
        payload = LeadSerializer(lead).data
        broadcast_lead_event(client_id=request.client.id, event="lead_updated", payload=payload)
        return Response(LeadSerializer(lead).data)

    @action(detail=True, methods=["post"], url_path="move")
    def move(self, request, pk=None):
        lead = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = LeadMoveSerializer(data=request.data, context={"request": request, "lead": lead})
        serializer.is_valid(raise_exception=True)
        target_stage = serializer.context["target_stage"]
        try:
            move_lead_to_stage(
                lead,
                stage=target_stage,
                created_by=request.user if request.user.is_authenticated else None,
                metadata={"source": "crm_move"},
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        lead.refresh_from_db()
        payload = LeadSerializer(lead).data
        broadcast_lead_event(client_id=request.client.id, event="lead_updated", payload=payload)
        return Response(payload, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="activities")
    def activities(self, request, pk=None):
        lead = get_object_or_404(self.get_queryset(), pk=pk)
        activities_qs = lead.activities.select_related("created_by").order_by("-created_at", "-id")
        serializer = LeadActivitySerializer(activities_qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="note")
    def note(self, request, pk=None):
        lead = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = LeadNoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        add_lead_note(
            lead,
            note=serializer.validated_data["note"],
            created_by=request.user if request.user.is_authenticated else None,
            metadata={"source": "crm_note"},
        )
        lead.refresh_from_db()
        payload = LeadSerializer(lead).data
        broadcast_lead_event(client_id=request.client.id, event="lead_updated", payload=payload)
        return Response(payload, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="schedule")
    def schedule(self, request, pk=None):
        lead = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = LeadScheduleSerializer(data=request.data, context={"request": request, "lead": lead})
        serializer.is_valid(raise_exception=True)
        schedule_lead_contact(
            lead,
            next_contact_at=serializer.validated_data["next_contact_at"],
            created_by=request.user if request.user.is_authenticated else None,
            description=serializer.validated_data.get("note") or "",
            metadata={"source": "crm_schedule"},
        )
        lead.refresh_from_db()
        payload = LeadSerializer(lead).data
        broadcast_lead_event(client_id=request.client.id, event="lead_updated", payload=payload)
        return Response(payload, status=status.HTTP_200_OK)


class WidgetVariantViewSet(viewsets.ModelViewSet):
    serializer_class = WidgetVariantSerializer
    permission_classes = [permissions.IsAuthenticated, IsClientUser, HasActiveSubscription]

    def get_queryset(self):
        return WidgetVariant.objects.filter(client=self.request.client).order_by("-is_active", "name")

    def perform_create(self, serializer):
        serializer.save(client=self.request.client)


class PublicWidgetVariantView(APIView):
    permission_classes = [HasValidApiKey]
    throttle_scope = "public_widget_variant"

    @staticmethod
    def _pick_variant(variants, *, seed: str):
        if not variants:
            return None
        if len(variants) == 1:
            return variants[0]
        digest = sha256(seed.encode("utf-8")).hexdigest()
        index = int(digest[:12], 16) % len(variants)
        return variants[index]

    def get(self, request):
        client = request.client
        variants = list(WidgetVariant.objects.filter(client=client, is_active=True).order_by("id"))
        if not variants:
            return Response({"variant": None, "items": []}, status=status.HTTP_200_OK)

        visitor_id = (request.query_params.get("visitor_id") or "").strip()
        session_id = (request.query_params.get("session_id") or "").strip()
        seed = f"{client.id}:{visitor_id or session_id or 'anonymous'}"
        variant = self._pick_variant(variants, seed=seed)

        track_impression = (request.query_params.get("track") or "1").lower() not in {"0", "false", "no"}
        if track_impression and variant:
            WidgetVariant.objects.filter(id=variant.id).update(impressions=F("impressions") + 1)
            variant.refresh_from_db()

        return Response(
            {
                "variant": WidgetVariantSerializer(variant).data if variant else None,
                "items": WidgetVariantSerializer(variants, many=True).data,
            },
            status=status.HTTP_200_OK,
        )


class PublicWidgetVariantImpressionView(APIView):
    permission_classes = [HasValidApiKey]
    throttle_scope = "public_widget_variant"

    def post(self, request):
        serializer = WidgetVariantImpressionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        variant_id = serializer.validated_data["variant_id"]
        updated = WidgetVariant.objects.filter(
            id=variant_id,
            client=request.client,
            is_active=True,
        ).update(impressions=F("impressions") + 1)
        return Response({"ok": bool(updated)}, status=status.HTTP_200_OK)
