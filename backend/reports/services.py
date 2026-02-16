import logging
import secrets
import string
from datetime import date, datetime, time, timedelta
from io import BytesIO
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from analytics_app.views import _build_summary_payload
from reports.models import ReportLog, ReportSettings, TelegramLinkToken

logger = logging.getLogger(__name__)

FONT_NAME = "TrackNodeUnicode"
FONT_PATH = Path(settings.BASE_DIR) / "static" / "fonts" / "Arial.ttf"
LOGO_PATH = Path(settings.BASE_DIR) / "static" / "reports" / "tracknode-logo.png"


def _ensure_font_registered():
    try:
        pdfmetrics.getFont(FONT_NAME)
    except KeyError:
        pdfmetrics.registerFont(TTFont(FONT_NAME, str(FONT_PATH)))


def _period_dt(period_from: date, period_to: date, tz_name: str):
    tz = ZoneInfo(tz_name)
    from_dt = timezone.make_aware(datetime.combine(period_from, time.min), tz)
    to_dt = timezone.make_aware(datetime.combine(period_to, time.max), tz)
    return from_dt, to_dt


def _default_manual_period():
    today = timezone.localdate()
    return today - timedelta(days=6), today


def _default_daily_period(tz_name: str):
    today = timezone.now().astimezone(ZoneInfo(tz_name)).date()
    yesterday = today - timedelta(days=1)
    return yesterday, yesterday


def collect_report_data(client, period_from: date, period_to: date, tz_name: str):
    from_dt, to_dt = _period_dt(period_from=period_from, period_to=period_to, tz_name=tz_name)
    payload = _build_summary_payload(client=client, from_dt=from_dt, to_dt=to_dt)
    payload["period_from"] = period_from
    payload["period_to"] = period_to
    return payload


def generate_pdf_bytes(client, user, report_data):
    _ensure_font_registered()

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=14 * mm,
        title="TrackNode Analytics Report",
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="RuTitle", parent=styles["Title"], fontName=FONT_NAME, fontSize=18, leading=22))
    styles.add(ParagraphStyle(name="RuH2", parent=styles["Heading2"], fontName=FONT_NAME, fontSize=12, leading=16))
    styles.add(ParagraphStyle(name="RuBody", parent=styles["BodyText"], fontName=FONT_NAME, fontSize=10, leading=14))
    styles.add(ParagraphStyle(name="RuSmall", parent=styles["BodyText"], fontName=FONT_NAME, fontSize=9, leading=12))

    elements = []
    if LOGO_PATH.exists():
        elements.append(Image(str(LOGO_PATH), width=78 * mm, height=18 * mm))
        elements.append(Spacer(1, 6))

    period_line = f"Период: {report_data['period_from'].strftime('%d.%m.%Y')} - {report_data['period_to'].strftime('%d.%m.%Y')}"
    elements.append(Paragraph("Отчёт TrackNode Analytics", styles["RuTitle"]))
    elements.append(Paragraph("Отчёт за вчера. Уникальные пользователи, Визиты, Заявки", styles["RuBody"]))
    elements.append(Paragraph(period_line, styles["RuBody"]))
    elements.append(Paragraph(f"Владелец: {user.email}", styles["RuSmall"]))
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("Основные KPI", styles["RuH2"]))
    kpi = [
        ["Визиты", str(report_data["visit_count"])],
        ["Уникальные пользователи", str(report_data["visitors_unique"])],
        ["Формы", str(report_data["form_submit_count"])],
        ["Заявки", str(report_data["leads_count"])],
        ["Конверсия", f"{round(float(report_data['conversion']) * 100, 2)}%"],
    ]
    kpi_table = Table(kpi, colWidths=[90 * mm, 70 * mm])
    kpi_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), FONT_NAME),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDF3FF")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#C4D5F5")),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    elements.append(kpi_table)
    elements.append(Spacer(1, 10))

    def add_table(title, headers, rows):
        elements.append(Paragraph(title, styles["RuH2"]))
        table_data = [headers] + rows if rows else [headers, ["Нет данных"] + ["-"] * (len(headers) - 1)]
        widths = [50 * mm] + [35 * mm] * (len(headers) - 1)
        table = Table(table_data, colWidths=widths[: len(headers)])
        table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), FONT_NAME),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EAF1FE")),
                    ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C9D7F2")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        elements.append(table)
        elements.append(Spacer(1, 8))

    top_sources_rows = [
        [item.get("source") or "direct", str(item.get("visits", 0)), str(item.get("leads", 0)), f"{item.get('conversion_pct', 0)}%"]
        for item in report_data.get("source_performance", [])[:10]
    ]
    add_table("Топ источников", ["Источник", "Визиты", "Заявки", "Конверсия"], top_sources_rows)

    top_click_rows = [
        [
            item.get("page_pathname") or "/",
            item.get("element_text") or item.get("element_id") or item.get("element_class") or "-",
            str(item.get("count", 0)),
            f"{item.get('percent_of_total', 0)}%",
        ]
        for item in report_data.get("top_clicks", [])[:10]
    ]
    add_table("Топ кликов", ["Страница", "Элемент", "Клики", "% от всех"], top_click_rows)

    by_pages_rows = [
        [item.get("pathname") or "/", str(item.get("visits", 0)), str(item.get("leads", 0)), f"{item.get('conversion_pct', 0)}%"]
        for item in report_data.get("conversion_by_pages", [])[:10]
    ]
    add_table("Конверсия по страницам", ["Страница", "Визиты", "Заявки", "Конверсия"], by_pages_rows)

    dynamics_rows = []
    by_day_visits = {str(item.get("day")): int(item.get("count") or 0) for item in report_data.get("visits_by_day", [])}
    by_day_unique = {str(item.get("day")): int(item.get("count") or 0) for item in report_data.get("unique_by_day", [])}
    by_day_forms = {str(item.get("day")): int(item.get("count") or 0) for item in report_data.get("forms_by_day", [])}
    by_day_leads = {str(item.get("day")): int(item.get("count") or 0) for item in report_data.get("leads_by_day", [])}
    all_days = sorted(set(by_day_visits.keys()) | set(by_day_unique.keys()) | set(by_day_forms.keys()) | set(by_day_leads.keys()))
    for day in all_days:
        dynamics_rows.append([day, str(by_day_unique.get(day, 0)), str(by_day_visits.get(day, 0)), str(by_day_forms.get(day, 0)), str(by_day_leads.get(day, 0))])
    add_table("Динамика по дням", ["Дата", "Уникальные", "Визиты", "Формы", "Заявки"], dynamics_rows)

    doc.build(elements)
    return buffer.getvalue()


def report_filename(client, period_from: date, period_to: date):
    return f"tracknode-report-client-{client.id}-{period_from:%Y%m%d}-{period_to:%Y%m%d}.pdf"


def save_report_file(filename: str, content: bytes):
    reports_dir = Path(getattr(settings, "REPORTS_STORAGE_DIR", settings.BASE_DIR / "reports_storage"))
    reports_dir.mkdir(parents=True, exist_ok=True)
    target = reports_dir / filename
    target.write_bytes(content)
    return str(target)


def send_report_email_to(email_to: str, filename: str, content: bytes, period_from: date, period_to: date):
    recipient = (email_to or "").strip()
    if not recipient:
        return False, "Email is empty"

    subject = f"Ваш отчёт TrackNode за {period_from.strftime('%d.%m.%Y')} - {period_to.strftime('%d.%m.%Y')}"
    body = (
        "Здравствуйте!\n\n"
        f"Во вложении PDF-отчёт TrackNode за период {period_from.strftime('%d.%m.%Y')} - {period_to.strftime('%d.%m.%Y')}.\n"
        "Ключевые KPI: Уникальные пользователи, Визиты, Формы, Заявки, Конверсия.\n\n"
        "TrackNode Analytics"
    )
    email = EmailMessage(subject=subject, body=body, to=[recipient])
    email.attach(filename, content, "application/pdf")
    try:
        sent = email.send(fail_silently=False)
        return (sent > 0), ""
    except Exception as exc:
        logger.exception("report.email send failed recipient=%s", recipient)
        return False, str(exc)


def _telegram_api_url(method: str) -> str:
    token = (getattr(settings, "TELEGRAM_BOT_TOKEN", "") or "").strip()
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is empty")
    return f"https://api.telegram.org/bot{token}/{method}"


def send_report_telegram(chat_id: str, filename: str, content: bytes, caption: str):
    if not chat_id:
        return False, "telegram chat_id is empty"
    try:
        response = requests.post(
            _telegram_api_url("sendDocument"),
            data={"chat_id": str(chat_id), "caption": caption},
            files={"document": (filename, content, "application/pdf")},
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        if not payload.get("ok"):
            return False, str(payload)
        return True, ""
    except Exception as exc:
        logger.exception("report.telegram send failed chat_id=%s", chat_id)
        return False, str(exc)


def get_or_create_settings(user, client):
    settings_obj, _ = ReportSettings.objects.get_or_create(
        user=user,
        client=client,
        defaults={"email_to": (user.email or "").strip() or None},
    )
    if not settings_obj.email_to and getattr(user, "email", None):
        settings_obj.email_to = user.email
        settings_obj.save(update_fields=["email_to", "updated_at"])
    return settings_obj


def log_report_result(*, user, client, period_from, period_to, status, trigger_type, file_path="", delivery_channels="", error=""):
    return ReportLog.objects.create(
        user=user,
        client=client,
        period_from=period_from,
        period_to=period_to,
        status=status,
        trigger_type=trigger_type,
        file_path=file_path,
        delivery_channels=delivery_channels,
        error=error,
    )


def _generate_link_code(length: int = 8) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def create_telegram_link_token(*, user, client, ttl_minutes: int = 10):
    expires_at = timezone.now() + timedelta(minutes=ttl_minutes)
    for _ in range(5):
        code = _generate_link_code(8)
        if not TelegramLinkToken.objects.filter(code=code, is_used=False, expires_at__gt=timezone.now()).exists():
            token = TelegramLinkToken.objects.create(user=user, client=client, code=code, expires_at=expires_at)
            bot_username = (getattr(settings, "TELEGRAM_BOT_USERNAME", "") or "").lstrip("@")
            start_link = f"https://t.me/{bot_username}" if bot_username else ""
            return token, start_link
    raise RuntimeError("Could not generate unique telegram link code")


def connect_telegram_by_code(*, code: str, chat_id: str, username: str | None = None):
    token = (
        TelegramLinkToken.objects.select_related("user", "client")
        .filter(code=(code or "").strip().upper(), is_used=False, expires_at__gt=timezone.now())
        .order_by("-created_at")
        .first()
    )
    if not token:
        return None, "Код недействителен или истёк."

    settings_obj = get_or_create_settings(token.user, token.client)
    settings_obj.telegram_chat_id = str(chat_id)
    settings_obj.telegram_username = (username or "").strip() or None
    settings_obj.telegram_is_connected = True
    settings_obj.save(update_fields=["telegram_chat_id", "telegram_username", "telegram_is_connected", "updated_at"])

    token.is_used = True
    token.save(update_fields=["is_used"])
    return settings_obj, ""


def disconnect_telegram(settings_obj: ReportSettings):
    settings_obj.send_telegram = False
    settings_obj.telegram_chat_id = None
    settings_obj.telegram_username = None
    settings_obj.telegram_is_connected = False
    settings_obj.save(update_fields=["send_telegram", "telegram_chat_id", "telegram_username", "telegram_is_connected", "updated_at"])


def deliver_report(*, settings_obj: ReportSettings, filename: str, pdf_bytes: bytes, period_from: date, period_to: date):
    errors = []
    channels_sent = []

    if settings_obj.send_email:
        ok, err = send_report_email_to(settings_obj.email_to or "", filename, pdf_bytes, period_from, period_to)
        if ok:
            channels_sent.append("email")
        else:
            errors.append(f"email: {err}")

    if settings_obj.send_telegram:
        caption = f"Отчёт TrackNode за {period_from.strftime('%d.%m.%Y')} - {period_to.strftime('%d.%m.%Y')}"
        ok, err = send_report_telegram(settings_obj.telegram_chat_id or "", filename, pdf_bytes, caption)
        if ok:
            channels_sent.append("telegram")
        else:
            errors.append(f"telegram: {err}")

    if not settings_obj.send_email and not settings_obj.send_telegram:
        errors.append("Не выбран ни один канал доставки")

    status = ReportLog.Status.SUCCESS if not errors else ReportLog.Status.ERROR
    return {
        "status": status,
        "channels_sent": channels_sent,
        "channels_label": ",".join(channels_sent),
        "error_text": "; ".join(errors),
    }
