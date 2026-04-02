from __future__ import annotations

from typing import Iterable

from django.db import transaction
from django.utils import timezone

from clients.models import Client
from leads.models import Lead, LeadActivity, Pipeline, PipelineStage

DEFAULT_PIPELINE_NAME = "Основная"
DEFAULT_STAGE_ITEMS: tuple[dict, ...] = (
    {"name": "Новый", "order": 1, "color": "#3B82F6", "is_closed_stage": False},
    {"name": "В работе", "order": 2, "color": "#06B6D4", "is_closed_stage": False},
    {"name": "Квалифицирован", "order": 3, "color": "#14B8A6", "is_closed_stage": False},
    {"name": "Предложение", "order": 4, "color": "#F59E0B", "is_closed_stage": False},
    {"name": "Сделка", "order": 5, "color": "#22C55E", "is_closed_stage": True},
)


@transaction.atomic
def ensure_default_pipeline(client: Client) -> Pipeline:
    pipeline = (
        Pipeline.objects.select_for_update()
        .filter(client=client, is_default=True)
        .first()
    )
    if pipeline is None:
        pipeline = Pipeline.objects.filter(client=client).order_by("id").first()
        if pipeline is None:
            pipeline = Pipeline.objects.create(client=client, name=DEFAULT_PIPELINE_NAME, is_default=True)
        elif not pipeline.is_default:
            pipeline.is_default = True
            pipeline.save(update_fields=["is_default", "updated_at"])

    existing_by_order = {item.order: item for item in PipelineStage.objects.filter(pipeline=pipeline)}
    for stage_data in DEFAULT_STAGE_ITEMS:
        order = int(stage_data["order"])
        stage = existing_by_order.get(order)
        if stage is None:
            PipelineStage.objects.create(pipeline=pipeline, **stage_data)
            continue
        fields_to_update: list[str] = []
        for field_name in ("name", "color", "is_closed_stage"):
            expected = stage_data[field_name]
            if getattr(stage, field_name) != expected:
                setattr(stage, field_name, expected)
                fields_to_update.append(field_name)
        if fields_to_update:
            stage.save(update_fields=fields_to_update)
    return pipeline


def get_default_stage(client: Client) -> PipelineStage:
    pipeline = ensure_default_pipeline(client)
    stage = (
        PipelineStage.objects.filter(pipeline=pipeline, is_active=True)
        .order_by("order", "id")
        .first()
    )
    if stage:
        return stage
    return PipelineStage.objects.filter(pipeline=pipeline).order_by("order", "id").first()


def ensure_lead_stage(lead: Lead) -> Lead:
    if lead.stage_id:
        return lead
    lead.stage = get_default_stage(lead.client)
    lead.status = Lead.Status.NEW
    lead.save(update_fields=["stage", "status", "updated_at"])
    return lead


def sync_lead_contacts(lead: Lead, *, normalized_phone: str, normalized_email: str) -> None:
    fields_to_update: list[str] = []
    if lead.normalized_phone != normalized_phone:
        lead.normalized_phone = normalized_phone
        fields_to_update.append("normalized_phone")
    if lead.normalized_email != normalized_email:
        lead.normalized_email = normalized_email
        fields_to_update.append("normalized_email")
    if fields_to_update:
        fields_to_update.append("updated_at")
        lead.save(update_fields=fields_to_update)


def log_lead_activity(
    lead: Lead,
    *,
    action_type: str,
    description: str = "",
    created_by=None,
    metadata: dict | None = None,
) -> LeadActivity:
    now = timezone.now()
    activity = LeadActivity.objects.create(
        lead=lead,
        action_type=action_type,
        description=description or "",
        created_by=created_by,
        metadata=metadata or {},
    )
    lead.last_activity_at = now
    lead.save(update_fields=["last_activity_at", "updated_at"])
    return activity


def _status_for_stage(stage: PipelineStage) -> str:
    if stage.is_closed_stage:
        return Lead.Status.CLOSED
    if stage.order <= 1:
        return Lead.Status.NEW
    return Lead.Status.IN_PROGRESS


@transaction.atomic
def move_lead_to_stage(
    lead: Lead,
    *,
    stage: PipelineStage,
    created_by=None,
    metadata: dict | None = None,
) -> Lead:
    if stage.pipeline.client_id != lead.client_id:
        raise ValueError("Lead and stage belong to different clients")

    prev_stage = lead.stage
    lead.stage = stage
    lead.status = _status_for_stage(stage)
    lead.save(update_fields=["stage", "status", "updated_at"])
    log_lead_activity(
        lead,
        action_type=LeadActivity.ActionType.STAGE_MOVED,
        created_by=created_by,
        description=f"Лид перемещен: {prev_stage.name if prev_stage else '—'} -> {stage.name}",
        metadata={
            "from_stage_id": prev_stage.id if prev_stage else None,
            "to_stage_id": stage.id,
            **(metadata or {}),
        },
    )
    return lead


def add_lead_note(lead: Lead, *, note: str, created_by=None, metadata: dict | None = None) -> LeadActivity:
    return log_lead_activity(
        lead,
        action_type=LeadActivity.ActionType.NOTE_ADDED,
        description=note,
        created_by=created_by,
        metadata=metadata or {},
    )


def schedule_lead_contact(
    lead: Lead,
    *,
    next_contact_at,
    created_by=None,
    description: str = "",
    metadata: dict | None = None,
) -> Lead:
    lead.next_contact_at = next_contact_at
    lead.save(update_fields=["next_contact_at", "updated_at"])
    log_lead_activity(
        lead,
        action_type=LeadActivity.ActionType.SCHEDULED,
        description=description or f"Следующий контакт запланирован на {next_contact_at.isoformat()}",
        created_by=created_by,
        metadata={"next_contact_at": next_contact_at.isoformat(), **(metadata or {})},
    )
    return lead


def bootstrap_default_pipelines_for_clients(clients: Iterable[Client]) -> None:
    for client in clients:
        ensure_default_pipeline(client)

