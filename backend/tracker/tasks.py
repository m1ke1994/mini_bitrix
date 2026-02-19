import logging
from urllib.parse import urlparse

from celery import shared_task
from django.utils import timezone

from clients.models import Client
from leads.services import send_telegram_message
from tracker.models import Event

logger = logging.getLogger(__name__)


def _safe_text(value, *, fallback: str = "-", max_len: int = 255) -> str:
    text = (value or "").strip()
    if not text:
        return fallback
    return text[:max_len]


def _field_names(payload: dict) -> str:
    raw_fields = payload.get("fields")
    if not isinstance(raw_fields, list):
        return ""

    names: list[str] = []
    for item in raw_fields:
        if not isinstance(item, dict):
            continue
        name = _safe_text(item.get("name"), fallback="", max_len=64)
        if not name:
            continue
        if name in names:
            continue
        names.append(name)
        if len(names) >= 8:
            break
    return ", ".join(names)


@shared_task
def send_tracker_form_submit_notification_task(event_id: int, client_id: int) -> None:
    try:
        event = Event.objects.select_related("visit", "visit__site").get(id=event_id)
        client = Client.objects.get(id=client_id, is_active=True)
    except (Event.DoesNotExist, Client.DoesNotExist):
        return

    if event.type != "form_submit":
        return
    if not client.send_to_telegram or not client.telegram_chat_id:
        return

    payload = event.payload if isinstance(event.payload, dict) else {}
    page_url = _safe_text(payload.get("page_url") or payload.get("url"), fallback="")
    page_path = _safe_text(payload.get("path"), fallback="")
    if not page_path and page_url:
        page_path = _safe_text(urlparse(page_url).path, fallback="/", max_len=256)
    if not page_path:
        page_path = "/"

    site_name = _safe_text(payload.get("domain"), fallback="")
    if not site_name and page_url:
        site_name = _safe_text(urlparse(page_url).netloc, fallback="", max_len=255)
    if not site_name:
        site_name = _safe_text(event.visit.site.domain, fallback="unknown", max_len=255)

    local_time = timezone.localtime(event.timestamp).strftime("%d.%m.%Y %H:%M")
    form_method = _safe_text(payload.get("method"), fallback="")
    form_action = _safe_text(payload.get("action"), fallback="")
    fields_text = _field_names(payload)

    lines = [
        "Новая заявка",
        "",
        f"Сайт: {site_name}",
        f"Страница: {page_path}",
        f"Время: {local_time}",
    ]

    if form_method:
        lines.append(f"Метод: {form_method}")
    if form_action:
        lines.append(f"Форма: {form_action}")
    if fields_text:
        lines.append(f"Поля: {fields_text}")

    try:
        send_telegram_message(client.telegram_chat_id, "\n".join(lines))
    except Exception:
        logger.exception(
            "tracker.form_submit telegram notify failed event_id=%s client_id=%s",
            event_id,
            client_id,
        )
