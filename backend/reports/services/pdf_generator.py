from datetime import datetime
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
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from analytics_app.services.metrics import default_period_days
from analytics_app.services.report_builder import build_full_report

FONT_NAME = "TrackNodeUnicode"
FONT_CANDIDATE_PATHS = [
    Path(settings.BASE_DIR) / "static" / "fonts" / "Arial.ttf",
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
]


def _ensure_font_registered():
    try:
        pdfmetrics.getFont(FONT_NAME)
    except KeyError:
        for font_path in FONT_CANDIDATE_PATHS:
            if font_path.exists():
                pdfmetrics.registerFont(TTFont(FONT_NAME, str(font_path)))
                return
        raise FileNotFoundError(
            "Unicode font not found for PDF generation. "
            "Expected one of: "
            + ", ".join(str(path) for path in FONT_CANDIDATE_PATHS)
        )


def _render_table(elements, title, headers, rows, widths, rows_per_page=28):
    elements.append(Paragraph(title, _styles()["h2"]))
    if not rows:
        rows = [["Нет данных"] + ["-"] * (len(headers) - 1)]

    start = 0
    while start < len(rows):
        chunk = rows[start : start + rows_per_page]
        table = Table([headers] + chunk, colWidths=widths)
        table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), FONT_NAME),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EAF7FC")),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B7DDEA")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        elements.append(table)
        start += rows_per_page
        if start < len(rows):
            elements.append(PageBreak())
            elements.append(Paragraph(f"{title} (продолжение)", _styles()["h2"]))
    elements.append(Spacer(1, 8))


def _styles():
    styles = getSampleStyleSheet()
    if "tn_title" not in styles:
        styles.add(ParagraphStyle(name="tn_title", parent=styles["Title"], fontName=FONT_NAME, fontSize=18, leading=22))
        styles.add(ParagraphStyle(name="tn_body", parent=styles["BodyText"], fontName=FONT_NAME, fontSize=10, leading=14))
        styles.add(ParagraphStyle(name="tn_h2", parent=styles["Heading2"], fontName=FONT_NAME, fontSize=12, leading=16))
    return {"title": styles["tn_title"], "body": styles["tn_body"], "h2": styles["tn_h2"]}


def _top_name_and_count(rows):
    if not rows:
        return "Нет данных", 0
    top = max(rows, key=lambda row: int(row.get("count") or 0))
    return top.get("name") or "Нет данных", int(top.get("count") or 0)


def build_pdf_for_client(*, client, user):
    date_from, date_to = default_period_days(days=14)
    report = build_full_report(client=client, date_from=date_from, date_to=date_to)
    summary = report["summary"]

    _ensure_font_registered()
    filename = f"tracknode-full-report-client-{client.id}-{timezone.localdate():%Y%m%d}.pdf"
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=14 * mm,
        bottomMargin=12 * mm,
        title="TrackNode Analytics - Полный отчёт по эффективности",
    )

    styles = _styles()
    elements = [
        Paragraph("TrackNode Analytics - Полный отчёт по эффективности", styles["title"]),
        Paragraph(f"Клиент: {client.name}. Владелец: {getattr(user, 'email', '-')}", styles["body"]),
        Paragraph(
            f"Период: {report['period']['date_from']:%d.%m.%Y} - {report['period']['date_to']:%d.%m.%Y}",
            styles["body"],
        ),
        Paragraph(f"Сформировано: {timezone.localtime(timezone.now()):%d.%m.%Y %H:%M}", styles["body"]),
        Spacer(1, 8),
    ]

    _render_table(
        elements,
        "Раздел 1. Ключевые метрики",
        ["Метрика", "Значение"],
        [
            ["Визиты", str(summary["visits"])],
            ["Уникальные пользователи", str(summary["unique_users"])],
            ["Отправки форм", str(summary["forms"])],
            ["Заявки", str(summary["leads"])],
            ["Конверсия", f"{summary['conversion']:.2f}%"],
        ],
        widths=[95 * mm, 70 * mm],
        rows_per_page=30,
    )

    top_device_name, top_device_count = _top_name_and_count(report["devices_distribution"]["devices"])
    top_os_name, top_os_count = _top_name_and_count(report["devices_distribution"]["os"])
    top_browser_name, top_browser_count = _top_name_and_count(report["devices_distribution"]["browsers"])
    _render_table(
        elements,
        "Сводка по устройствам (первая страница)",
        ["Категория", "Топ", "Количество"],
        [
            ["Устройство", top_device_name, str(top_device_count)],
            ["Операционная система", top_os_name, str(top_os_count)],
            ["Браузер", top_browser_name, str(top_browser_count)],
        ],
        widths=[45 * mm, 85 * mm, 35 * mm],
        rows_per_page=30,
    )

    daily_rows = [
        [
            row["day"].strftime("%d.%m.%Y"),
            str(row["visits"]),
            str(row["unique_users"]),
            str(row["forms"]),
            str(row["leads"]),
            f"{row['conversion']:.2f}%",
        ]
        for row in report["daily_stats"]
    ]
    _render_table(
        elements,
        "Раздел 2. Динамика по дням",
        ["Дата", "Визиты", "Уникальные", "Формы", "Заявки", "Конверсия"],
        daily_rows,
        widths=[30 * mm, 24 * mm, 28 * mm, 24 * mm, 24 * mm, 30 * mm],
        rows_per_page=24,
    )

    page_rows = [
        [
            row["pathname"],
            str(row["visits"]),
            str(row["leads"]),
            f"{row['conversion_pct']:.2f}%",
        ]
        for row in report["page_conversion"]
    ]
    _render_table(
        elements,
        "Раздел 3. Конверсия по страницам",
        ["Страница", "Визиты", "Заявки", "Конверсия %"],
        page_rows,
        widths=[95 * mm, 22 * mm, 22 * mm, 26 * mm],
        rows_per_page=24,
    )

    click_rows = []
    for row in report["top_clicks"]:
        element = row["element_text"] or row["element_id"] or row["element_class"] or "-"
        click_rows.append([row["page_pathname"], element[:50], str(row["count"]), f"{row['percent_of_total']:.2f}%"])
    _render_table(
        elements,
        "Раздел 4. Топ кликов",
        ["Страница", "Элемент", "Клики", "% от всех кликов"],
        click_rows,
        widths=[68 * mm, 58 * mm, 18 * mm, 21 * mm],
        rows_per_page=24,
    )

    source_rows = [[row["source"], str(row["visits"]), f"{row['percent_of_total']:.2f}%"] for row in report["sources"]]
    _render_table(
        elements,
        "Раздел 5. Топ источников",
        ["Источник", "Визиты", "% от общего"],
        source_rows,
        widths=[105 * mm, 30 * mm, 30 * mm],
        rows_per_page=28,
    )

    devices_rows = [[row["name"], str(row["count"]), f"{row['percent']:.2f}%"] for row in report["devices_distribution"]["devices"]]
    _render_table(
        elements,
        "Раздел 6. Распределение устройств - Тип устройства",
        ["Тип устройства", "Количество", "%"],
        devices_rows,
        widths=[95 * mm, 35 * mm, 35 * mm],
        rows_per_page=28,
    )

    os_rows = [[row["name"], str(row["count"]), f"{row['percent']:.2f}%"] for row in report["devices_distribution"]["os"]]
    _render_table(
        elements,
        "Раздел 6. Распределение устройств - Операционная система",
        ["Операционная система", "Количество", "%"],
        os_rows,
        widths=[95 * mm, 35 * mm, 35 * mm],
        rows_per_page=28,
    )

    browser_rows = [[row["name"], str(row["count"]), f"{row['percent']:.2f}%"] for row in report["devices_distribution"]["browsers"]]
    _render_table(
        elements,
        "Раздел 6. Распределение устройств - Браузер",
        ["Браузер", "Количество", "%"],
        browser_rows,
        widths=[95 * mm, 35 * mm, 35 * mm],
        rows_per_page=28,
    )

    leads_rows = [
        [
            str(row.get("id", "")),
            row.get("name") or "-",
            row.get("phone") or "-",
            row.get("email") or "-",
            timezone.localtime(datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))).strftime("%d.%m.%Y %H:%M")
            if row.get("created_at")
            else "-",
        ]
        for row in report["leads"]
    ]
    _render_table(
        elements,
        "Раздел 7. Последние заявки",
        ["ID", "Имя", "Телефон", "Email", "Дата"],
        leads_rows,
        widths=[12 * mm, 38 * mm, 32 * mm, 48 * mm, 35 * mm],
        rows_per_page=22,
    )

    doc.build(elements)
    return buffer.getvalue(), filename
