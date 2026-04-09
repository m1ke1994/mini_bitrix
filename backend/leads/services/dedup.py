from __future__ import annotations

from dataclasses import dataclass

from django.db.models import Q

from leads.crm import ensure_lead_stage, log_lead_activity
from leads.models import Lead, LeadActivity


@dataclass
class DeduplicationResult:
    lead: Lead
    created: bool
    merged: bool


class BaseLeadDeduplicationStrategy:
    def upsert(self, *, client, payload: dict, create_lead_fn):  # pragma: no cover - interface
        raise NotImplementedError


class MergeLeadDeduplicationStrategy(BaseLeadDeduplicationStrategy):
    def find_existing(self, *, client, normalized_phone: str, normalized_email: str) -> Lead | None:
        predicates = Q()
        if normalized_phone:
            predicates |= Q(normalized_phone=normalized_phone)
        if normalized_email:
            predicates |= Q(normalized_email=normalized_email)
        if not predicates:
            return None
        return (
            Lead.objects.filter(client=client)
            .filter(predicates)
            .select_related("stage")
            .order_by("-created_at", "-id")
            .first()
        )

    def _merge_payload_into_lead(self, *, lead: Lead, payload: dict) -> list[str]:
        fields_to_update: list[str] = []

        def update_if_empty(field_name: str):
            incoming = payload.get(field_name)
            if incoming in (None, "", " "):
                return
            current = getattr(lead, field_name)
            if current in (None, "", " "):
                setattr(lead, field_name, incoming)
                fields_to_update.append(field_name)

        for field_name in ("name", "phone", "email", "source_url", "utm_source", "utm_medium", "utm_campaign"):
            update_if_empty(field_name)

        for field_name in ("normalized_phone", "normalized_email", "session_id", "visitor_id"):
            update_if_empty(field_name)

        incoming_message = (payload.get("message") or "").strip()
        existing_message = (lead.message or "").strip()
        if incoming_message:
            if not existing_message:
                lead.message = incoming_message
                fields_to_update.append("message")
            elif incoming_message != existing_message and incoming_message not in existing_message:
                lead.message = f"{existing_message}\n\n---\n{incoming_message}"
                fields_to_update.append("message")

        return fields_to_update

    def upsert(self, *, client, payload: dict, create_lead_fn) -> DeduplicationResult:
        existing = self.find_existing(
            client=client,
            normalized_phone=(payload.get("normalized_phone") or ""),
            normalized_email=(payload.get("normalized_email") or ""),
        )
        if existing is None:
            lead = create_lead_fn(payload)
            ensure_lead_stage(lead)
            return DeduplicationResult(lead=lead, created=True, merged=False)

        fields_to_update = self._merge_payload_into_lead(lead=existing, payload=payload)
        if fields_to_update:
            fields_to_update.append("updated_at")
            existing.save(update_fields=fields_to_update)
        ensure_lead_stage(existing)
        log_lead_activity(
            existing,
            action_type=LeadActivity.ActionType.DUPLICATE_MERGED,
            description="Входящий лид объединен с существующим дубликатом",
            metadata={
                "strategy": "merge",
                "updated_fields": fields_to_update,
            },
        )
        return DeduplicationResult(lead=existing, created=False, merged=True)

