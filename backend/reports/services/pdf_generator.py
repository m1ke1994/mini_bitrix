from datetime import timedelta
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from analytics_app.views import _build_summary_payload

FONT_NAME = "TrackNodeUnicode"
FONT_PATH = Path(settings.BASE_DIR) / "static" / "fonts" / "Arial.ttf"


def _ensure_font_registered():
    try:
        pdfmetrics.getFont(FONT_NAME)
    except KeyError:
        pdfmetrics.registerFont(TTFont(FONT_NAME, str(FONT_PATH)))


def _collect_client_data(client):
    now = timezone.now()
    from_dt = now - timedelta(days=1)
    payload = _build_summary_payload(client=client, from_dt=from_dt, to_dt=now)
    return payload, from_dt, now


def build_pdf_for_client(*, client, user):
    payload, from_dt, to_dt = _collect_client_data(client)
    _ensure_font_registered()

    filename = f"tracknode-report-client-{client.id}-{timezone.localdate():%Y%m%d}.pdf"
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
    styles.add(ParagraphStyle(name="RuBody", parent=styles["BodyText"], fontName=FONT_NAME, fontSize=10, leading=14))
    styles.add(ParagraphStyle(name="RuH2", parent=styles["Heading2"], fontName=FONT_NAME, fontSize=12, leading=16))

    elements = [
        Paragraph("PDF отчёт TrackNode Analytics", styles["RuTitle"]),
        Paragraph(
            f"Клиент: {client.name}. Владелец: {getattr(user, 'email', '-')}.",
            styles["RuBody"],
        ),
        Paragraph(
            f"Период данных: {from_dt.astimezone(timezone.get_current_timezone()):%d.%m.%Y %H:%M} - "
            f"{to_dt.astimezone(timezone.get_current_timezone()):%d.%m.%Y %H:%M}",
            styles["RuBody"],
        ),
        Spacer(1, 8),
        Paragraph("Ключевые показатели", styles["RuH2"]),
    ]

    kpi = [
        ["Метрика", "Значение"],
        ["Визиты", str(payload.get("visit_count", 0))],
        ["Уникальные пользователи", str(payload.get("visitors_unique", 0))],
        ["Отправки форм", str(payload.get("form_submit_count", 0))],
        ["Заявки", str(payload.get("leads_count", 0))],
        ["Конверсия", f"{round(float(payload.get('conversion', 0.0)) * 100, 2)}%"],
    ]
    table = Table(kpi, colWidths=[90 * mm, 70 * mm])
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), FONT_NAME),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EAF7FC")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#B7DDEA")),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    elements.append(table)

    doc.build(elements)
    return buffer.getvalue(), filename
