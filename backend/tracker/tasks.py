import logging
from html import escape
from urllib.parse import urlparse

from celery import shared_task
from django.utils import timezone

from clients.models import Client
from leads.services import send_telegram_message
from tracker.models import Event

logger = logging.getLogger(__name__)


def _safe_text(value, *, fallback: str = "-", max_len: int = 1024) -> str:
    text = (value or "").strip()
    if not text:
        return fallback
    return text[:max_len]


def _escape_html(value: str) -> str:
    return escape(value, quote=True)


def _field_names(payload: dict) -> list[str]:
    raw_fields = payload.get("fields")
    if not isinstance(raw_fields, list):
        return []

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
        if len(names) >= 12:
            break
    return names


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
        parsed_page_url = urlparse(page_url)
        page_path = _safe_text(parsed_page_url.path, fallback="/", max_len=256)
        if parsed_page_url.query:
            page_path = f"{page_path}?{parsed_page_url.query}"[:512]
    if not page_path:
        page_path = "/"

    site_name = _safe_text(payload.get("domain"), fallback="")
    if not site_name and page_url:
        site_name = _safe_text(urlparse(page_url).netloc, fallback="", max_len=255)
    if not site_name:
        site_name = _safe_text(event.visit.site.domain, fallback="unknown", max_len=255)

    local_time = timezone.localtime(event.timestamp).strftime("%d.%m.%Y %H:%M")
    form_method = _safe_text(payload.get("method"), fallback="-", max_len=16).upper()
    form_action = _safe_text(payload.get("action"), fallback="-", max_len=1024)
    field_names = _field_names(payload)

    site_name_html = _escape_html(site_name)
    page_path_html = _escape_html(page_path)
    local_time_html = _escape_html(local_time)
    form_method_html = _escape_html(form_method)
    form_action_html = _escape_html(form_action)

    lines = [
        "📥 <b>Новый лид</b>",
        "",
        f"🌐 <b>Сайт:</b> <code>{site_name_html}</code>",
        f"📄 <b>Страница:</b> <code>{page_path_html}</code>",
        f"🕒 <b>Время:</b> {local_time_html}",
        f"⚙️ <b>Метод:</b> {form_method_html}",
        "",
        "🧾 <b>Форма:</b>",
        form_action_html,
        "",
        "📝 <b>Поля формы:</b>",
    ]

    if field_names:
        for field_name in field_names:
            lines.append(f"• {_escape_html(field_name)}")
    else:
        lines.append("• —")

    try:
        send_telegram_message(client.telegram_chat_id, "\n".join(lines), parse_mode="HTML")
    except Exception:
        logger.exception(
            "tracker.form_submit telegram notify failed event_id=%s client_id=%s",
            event_id,
            client_id,
        )
