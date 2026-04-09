from __future__ import annotations

import logging
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from leads.crm import log_lead_activity
from leads.models import Lead, LeadActivity
from leads.services import (
    format_lead_notification,
    send_lead_email,
    send_lead_webhook,
    send_telegram_message,
)
from leads.services.lead_scoring import LeadScoringService

logger = logging.getLogger(__name__)


def _send_notification_channels(lead: Lead) -> dict:
    client = lead.client
    delivered = {
        "telegram": False,
        "email": False,
        "webhook": False,
    }

    if client.send_to_telegram and client.telegram_chat_id:
        try:
            delivered["telegram"] = send_telegram_message(client.telegram_chat_id, format_lead_notification(lead))
        except Exception:
            logger.exception("Telegram notification failed lead_id=%s", lead.id)

    if (client.notification_email or "").strip():
        delivered["email"] = send_lead_email(client.notification_email.strip(), lead)

    if (client.webhook_url or "").strip():
        delivered["webhook"] = send_lead_webhook(
            client.webhook_url.strip(),
            lead,
            timeout=max(2, int(client.webhook_timeout_seconds or 10)),
        )

    return delivered


@shared_task
def notify_new_lead(lead_id: int) -> None:
    try:
        lead = Lead.objects.select_related("client", "stage").get(id=lead_id)
    except Lead.DoesNotExist:
        return

    delivered = _send_notification_channels(lead)
    if any(delivered.values()):
        log_lead_activity(
            lead,
            action_type=LeadActivity.ActionType.NOTIFIED,
            description="Отправлены уведомления о новом лиде",
            metadata={"channels": delivered, "kind": "new_lead"},
        )


@shared_task
def check_stale_leads() -> int:
    now = timezone.now()
    checked = 0
    for lead in Lead.objects.select_related("client", "stage").filter(stage__is_closed_stage=False):
        client = lead.client
        stale_hours = max(1, int(client.stale_lead_hours or 24))
        boundary = now - timedelta(hours=stale_hours)
        last_touch = lead.last_activity_at or lead.created_at
        if last_touch and last_touch > boundary:
            continue

        latest_stale_notify = (
            lead.activities.filter(
                action_type=LeadActivity.ActionType.NOTIFIED,
                metadata__kind="stale_lead",
            )
            .order_by("-created_at")
            .first()
        )
        if latest_stale_notify and latest_stale_notify.created_at >= now - timedelta(hours=6):
            continue

        checked += 1
        delivered = _send_notification_channels(lead)
        if any(delivered.values()):
            log_lead_activity(
                lead,
                action_type=LeadActivity.ActionType.NOTIFIED,
                description=f"Напоминание: лид без активности более {stale_hours}ч",
                metadata={"channels": delivered, "kind": "stale_lead", "stale_hours": stale_hours},
            )
    return checked


def _render_auto_response(client, lead: Lead) -> tuple[str, str]:
    subject = (client.auto_respond_subject or "").strip() or "Спасибо за заявку"
    template = (client.auto_respond_template or "").strip() or (
        "Здравствуйте, {name}!\n\n"
        "Мы получили вашу заявку и скоро свяжемся с вами.\n"
        "С уважением,\n"
        "{client_name}"
    )
    message = template.format(
        name=(lead.name or "клиент").strip() or "клиент",
        client_name=client.name,
        lead_id=lead.id,
    )
    return subject, message


@shared_task
def auto_respond_lead(lead_id: int) -> None:
    try:
        lead = Lead.objects.select_related("client").get(id=lead_id)
    except Lead.DoesNotExist:
        return

    client = lead.client
    if not client.auto_respond_enabled:
        return
    if not (lead.email or "").strip():
        return

    subject, message = _render_auto_response(client, lead)
    sent = False
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[lead.email.strip()],
            fail_silently=False,
        )
        sent = True
    except Exception:
        logger.exception("Auto respond send failed lead_id=%s", lead.id)
        sent = False

    if sent:
        log_lead_activity(
            lead,
            action_type=LeadActivity.ActionType.AUTO_RESPONSE,
            description="Отправлен автоответ клиенту",
            metadata={"channel": "email", "subject": subject, "preview": message[:200]},
        )


# Backward compatible task name.
@shared_task(name="leads.tasks.send_lead_notification_task")
def send_lead_notification_task(lead_id: int) -> None:
    notify_new_lead.delay(lead_id)


@shared_task
def recalculate_lead_score_for_session(client_id: int, session_id: str = "", visitor_id: str = "") -> int:
    sid = (session_id or "").strip()
    vid = (visitor_id or "").strip()
    if not sid and not vid:
        return 0

    queryset = Lead.objects.filter(client_id=client_id)
    if sid:
        queryset = queryset.filter(session_id=sid)
    else:
        queryset = queryset.filter(visitor_id=vid)

    updated = 0
    for lead in queryset.iterator():
        before = int(lead.score or 0)
        after = LeadScoringService.apply(lead, session_id=sid or lead.session_id, visitor_id=vid or lead.visitor_id)
        if after != before:
            updated += 1
    return updated
