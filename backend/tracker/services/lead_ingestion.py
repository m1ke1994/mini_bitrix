from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse

from django.db import IntegrityError, transaction
from django.db.models import F

from analytics_app.models import PageView as AnalyticsPageView
from clients.models import Client
from leads.crm import get_default_stage, log_lead_activity
from leads.models import Lead, LeadActivity
from leads.realtime import broadcast_lead_event
from leads.services.lead_scoring import LeadScoringService
from leads.services.notifications import serialize_lead
from leads.utils import normalize_email, normalize_phone, normalize_phone_for_dedup
from tracker.models import Event as TrackerEvent
from tracker.models import Site

logger = logging.getLogger(__name__)

TRACKER_CONVERSION_EVENT_TYPES = {"form_submit_success", "conversion"}
LEAD_NAME_FALLBACK = "Заявка с сайта"


@dataclass
class TrackerLeadIngestionResult:
    lead: Lead
    created: bool
    deduplicated: bool


def _clean_text(value, *, max_len: int = 1000) -> str:
    text = str(value or "").strip()
    return text[:max_len]


def _clean_message(value) -> str:
    text = str(value or "").strip()
    return text[:4000]


def _first_non_empty(*values, max_len: int = 1000):
    for value in values:
        cleaned = _clean_text(value, max_len=max_len)
        if cleaned:
            return cleaned
    return ""


def _to_url_or_blank(value) -> str:
    raw = _clean_text(value, max_len=1000)
    if not raw:
        return ""
    parsed = urlparse(raw)
    if parsed.scheme and parsed.netloc:
        return raw
    return ""


def _extract_utm_from_url(source_url: str) -> dict[str, str]:
    if not source_url:
        return {}
    try:
        parsed = urlparse(source_url)
        query = parse_qs(parsed.query or "")
    except Exception:
        return {}
    return {
        "utm_source": _clean_text((query.get("utm_source") or [""])[0], max_len=255),
        "utm_medium": _clean_text((query.get("utm_medium") or [""])[0], max_len=255),
        "utm_campaign": _clean_text((query.get("utm_campaign") or [""])[0], max_len=255),
    }


def _status_for_stage(stage) -> str:
    if not stage:
        return Lead.Status.NEW
    if stage.is_closed_stage:
        return Lead.Status.CLOSED
    if int(stage.order or 0) <= 1:
        return Lead.Status.NEW
    return Lead.Status.IN_PROGRESS


def _event_should_create_lead(event_type: str) -> bool:
    return (event_type or "").strip().lower() in TRACKER_CONVERSION_EVENT_TYPES


def _extract_contact_payload(payload: dict) -> dict:
    lead_data = payload.get("lead_data")
    if not isinstance(lead_data, dict):
        lead_data = {}

    name = _first_non_empty(
        lead_data.get("name"),
        payload.get("name"),
        payload.get("contact_name"),
        max_len=255,
    )
    phone_raw = _first_non_empty(
        lead_data.get("phone"),
        lead_data.get("contact"),
        payload.get("phone"),
        payload.get("contact"),
        max_len=80,
    )
    email_raw = _first_non_empty(
        lead_data.get("email"),
        payload.get("email"),
        max_len=255,
    )
    message = _first_non_empty(
        lead_data.get("message"),
        payload.get("message"),
        payload.get("comment"),
        max_len=4000,
    )

    normalized_email = normalize_email(email_raw) or ""
    normalized_phone = normalize_phone_for_dedup(phone_raw)
    phone = normalize_phone(phone_raw)

    return {
        "name": name,
        "phone": phone or None,
        "normalized_phone": normalized_phone,
        "email": normalized_email or None,
        "normalized_email": normalized_email,
        "message": _clean_message(message) or None,
    }


def _build_tracker_dedup_key(
    *,
    event: TrackerEvent,
    payload: dict,
    submission_id: str,
    source_url: str,
) -> str:
    if submission_id:
        seed = f"submission:{submission_id.lower()}"
    else:
        seed = "|".join(
            [
                _clean_text(event.type, max_len=80).lower(),
                _clean_text(event.visit.session_id, max_len=64),
                _clean_text(event.visit.visitor_id, max_len=64),
                _clean_text(payload.get("form_key") or payload.get("id"), max_len=180).lower(),
                _clean_text(source_url, max_len=1000).lower(),
                event.timestamp.isoformat(),
            ]
        )
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


def _merge_lead_if_empty(lead: Lead, incoming: dict) -> list[str]:
    fields_to_update: list[str] = []

    for field_name in (
        "name",
        "phone",
        "normalized_phone",
        "email",
        "normalized_email",
        "message",
        "source_url",
        "utm_source",
        "utm_medium",
        "utm_campaign",
        "session_id",
        "visitor_id",
        "tracker_submission_id",
    ):
        incoming_value = incoming.get(field_name)
        if incoming_value in (None, "", " "):
            continue
        current_value = getattr(lead, field_name)
        if current_value in (None, "", " "):
            setattr(lead, field_name, incoming_value)
            fields_to_update.append(field_name)

    return fields_to_update


def ingest_tracker_lead_from_event(
    *,
    event: TrackerEvent,
    site: Site,
    client: Client,
) -> TrackerLeadIngestionResult | None:
    if not event or not client or not site:
        return None
    if not _event_should_create_lead(event.type):
        return None

    payload = event.payload if isinstance(event.payload, dict) else {}

    submission_id = _clean_text(payload.get("submission_id"), max_len=128)
    source_url = _to_url_or_blank(
        payload.get("page_url")
        or payload.get("url")
        or payload.get("request_url")
    )
    utm_from_url = _extract_utm_from_url(source_url)
    referrer = _clean_text(payload.get("referrer"), max_len=1000) or _clean_text(event.visit.referrer, max_len=1000)

    contact = _extract_contact_payload(payload)
    dedup_key = _build_tracker_dedup_key(
        event=event,
        payload=payload,
        submission_id=submission_id,
        source_url=source_url,
    )

    default_stage = None
    try:
        default_stage = get_default_stage(client)
    except Exception:
        logger.exception("tracker.lead_ingestion failed to resolve default stage client_id=%s", client.id)

    defaults = {
        "client": client,
        "name": contact["name"] or LEAD_NAME_FALLBACK,
        "phone": contact["phone"],
        "normalized_phone": contact["normalized_phone"],
        "email": contact["email"],
        "normalized_email": contact["normalized_email"],
        "message": contact["message"],
        "source_url": source_url or None,
        "utm_source": _first_non_empty(payload.get("utm_source"), utm_from_url.get("utm_source"), max_len=255) or None,
        "utm_medium": _first_non_empty(payload.get("utm_medium"), utm_from_url.get("utm_medium"), max_len=255) or None,
        "utm_campaign": _first_non_empty(payload.get("utm_campaign"), utm_from_url.get("utm_campaign"), max_len=255) or None,
        "session_id": _clean_text(event.visit.session_id, max_len=64),
        "visitor_id": _clean_text(event.visit.visitor_id, max_len=64),
        "stage": default_stage,
        "status": _status_for_stage(default_stage),
        "tracker_submission_id": submission_id,
        "tracker_dedup_key": dedup_key,
    }

    created = False
    lead = None
    updated_fields: list[str] = []
    try:
        with transaction.atomic():
            lead = Lead.objects.select_for_update().filter(client=client, tracker_dedup_key=dedup_key).first()
            if lead is None:
                lead = Lead.objects.create(**defaults)
                created = True
            else:
                updated_fields = _merge_lead_if_empty(lead, defaults)
                if not lead.stage_id and default_stage:
                    lead.stage = default_stage
                    lead.status = _status_for_stage(default_stage)
                    updated_fields.extend(["stage", "status"])
                if updated_fields:
                    updated_fields.append("updated_at")
                    lead.save(update_fields=sorted(set(updated_fields)))
    except IntegrityError:
        lead = Lead.objects.filter(client=client, tracker_dedup_key=dedup_key).select_related("stage").first()
        created = False
        updated_fields = []

    if not lead:
        return None

    if created:
        log_lead_activity(
            lead,
            action_type=LeadActivity.ActionType.CREATED,
            description="Лид создан из tracker.js (успешная отправка формы)",
            metadata={
                "source": "tracker_event",
                "event_id": event.id,
                "event_type": event.type,
                "site_id": site.id,
                "site_domain": site.domain,
                "submission_id": submission_id or None,
                "dedup_key": dedup_key,
                "referrer": referrer or None,
            },
        )

        if lead.session_id:
            latest_page_view = (
                AnalyticsPageView.objects.filter(client=client, session_id=lead.session_id)
                .order_by("-created_at")
                .first()
            )
            if latest_page_view:
                AnalyticsPageView.objects.filter(id=latest_page_view.id).update(attributed_leads=F("attributed_leads") + 1)

        try:
            from leads.tasks import auto_respond_lead, notify_new_lead  # local import to avoid circular dependency

            notify_new_lead.delay(lead.id)
            auto_respond_lead.delay(lead.id)
        except Exception:
            logger.exception("tracker.lead_ingestion failed to enqueue lead tasks lead_id=%s", lead.id)

    LeadScoringService.apply(
        lead,
        session_id=lead.session_id,
        visitor_id=lead.visitor_id,
        log_reason="tracker_event",
    )
    lead.refresh_from_db()

    if created or updated_fields:
        broadcast_lead_event(
            client_id=client.id,
            event="lead_created" if created else "lead_updated",
            payload=serialize_lead(lead),
        )

    logger.info(
        "tracker.lead_ingestion event_id=%s client_id=%s site_id=%s lead_id=%s created=%s dedup=%s",
        event.id,
        client.id,
        site.id,
        lead.id,
        created,
        not created,
    )
    return TrackerLeadIngestionResult(lead=lead, created=created, deduplicated=not created)
