from __future__ import annotations

import logging

import requests
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from leads.models import Lead

logger = logging.getLogger(__name__)


def send_telegram_message(chat_id: str, message: str, parse_mode: str | None = None) -> bool:
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        logger.info("Telegram token is not configured, skipping message.")
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    if parse_mode:
        payload["parse_mode"] = parse_mode
        payload["disable_web_page_preview"] = True
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        body = response.json()
        if not body.get("ok"):
            logger.warning("Telegram sendMessage not ok: chat_id=%s payload=%s", chat_id, body)
            return False
        return True
    except requests.RequestException:
        logger.exception("Failed to send telegram message for chat_id=%s", chat_id)
        return False


def serialize_lead(lead: Lead) -> dict:
    stage_name = lead.stage.name if lead.stage_id else None
    stage_color = lead.stage.color if lead.stage_id else None
    return {
        "id": lead.id,
        "client_id": lead.client_id,
        "name": (lead.name or "").strip() or None,
        "phone": (lead.phone or "").strip() or None,
        "email": (lead.email or "").strip() or None,
        "message": (lead.message or "").strip() or None,
        "source_url": lead.source_url,
        "utm_source": lead.utm_source,
        "utm_medium": lead.utm_medium,
        "utm_campaign": lead.utm_campaign,
        "status": lead.status,
        "score": int(lead.score or 0),
        "stage": stage_name,
        "stage_id": lead.stage_id,
        "stage_name": stage_name,
        "stage_color": stage_color,
        "next_contact_at": lead.next_contact_at.isoformat() if lead.next_contact_at else None,
        "last_activity_at": lead.last_activity_at.isoformat() if lead.last_activity_at else None,
        "created_at": timezone.localtime(lead.created_at).isoformat(),
        "updated_at": timezone.localtime(lead.updated_at).isoformat() if lead.updated_at else None,
    }


def format_lead_notification(lead: Lead) -> str:
    local_created_at = timezone.localtime(lead.created_at)
    source_value = lead.source_url or lead.utm_source or lead.utm_campaign or "не указано"
    name_value = (lead.name or "").strip() or "не указано"
    phone_value = (lead.phone or "").strip() or "не указан"
    email_value = (lead.email or "").strip() or "не указан"
    stage_value = lead.stage.name if lead.stage_id else "Новый"

    return "\n".join(
        [
            "Новый лид",
            "",
            f"Клиент: {lead.client.name}",
            f"Стадия: {stage_value}",
            f"Score: {lead.score}",
            f"Источник: {source_value}",
            f"Время: {local_created_at.strftime('%d.%m.%Y %H:%M (%Z)')}",
            "",
            f"Имя: {name_value}",
            f"Телефон: {phone_value}",
            f"Email: {email_value}",
            "",
            "Сообщение:",
            (lead.message or "не указано"),
        ]
    )


def format_lead_email(lead: Lead) -> str:
    payload = serialize_lead(lead)
    return (
        "Новый лид в TrackNode\n\n"
        f"ID: {payload['id']}\n"
        f"Клиент: {lead.client.name}\n"
        f"Стадия: {payload['stage'] or 'Новый'}\n"
        f"Score: {payload['score']}\n"
        f"Имя: {payload['name'] or '-'}\n"
        f"Телефон: {payload['phone'] or '-'}\n"
        f"Email: {payload['email'] or '-'}\n"
        f"Источник: {payload['source_url'] or payload['utm_source'] or '-'}\n"
        f"Сообщение: {payload['message'] or '-'}\n"
    )


def send_lead_email(recipient: str, lead: Lead) -> bool:
    if not recipient:
        return False
    try:
        send_mail(
            subject=f"Новый лид: {(lead.name or 'Без имени').strip() or 'Без имени'}",
            message=format_lead_email(lead),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )
        return True
    except Exception:
        logger.exception("Failed to send lead email recipient=%s lead_id=%s", recipient, lead.id)
        return False


def send_lead_webhook(url: str, lead: Lead, *, timeout: int = 10) -> bool:
    if not url:
        return False
    try:
        response = requests.post(
            url,
            json=serialize_lead(lead),
            timeout=max(2, int(timeout)),
            headers={"Content-Type": "application/json"},
        )
        if 200 <= response.status_code < 300:
            return True
        logger.warning(
            "Lead webhook returned non-2xx status=%s lead_id=%s url=%s body=%s",
            response.status_code,
            lead.id,
            url,
            response.text[:500],
        )
        return False
    except requests.RequestException:
        logger.exception("Lead webhook failed lead_id=%s url=%s", lead.id, url)
        return False
