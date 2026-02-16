import logging
from zoneinfo import ZoneInfo

from celery import shared_task
from django.utils import timezone

from reports.models import ReportLog, ReportSettings
from reports.services import (
    _default_daily_period,
    collect_report_data,
    deliver_report,
    generate_pdf_bytes,
    log_report_result,
    report_filename,
    save_report_file,
)

logger = logging.getLogger(__name__)


@shared_task
def send_daily_reports_task() -> int:
    now_utc = timezone.now()
    processed = 0
    candidates = ReportSettings.objects.select_related("user", "client").filter(enabled=True)
    for settings_obj in candidates:
        try:
            tz = ZoneInfo(settings_obj.timezone)
        except Exception:
            tz = ZoneInfo("Europe/Moscow")

        local_now = now_utc.astimezone(tz)
        target_time = settings_obj.daily_time
        delta_minutes = abs((local_now.hour * 60 + local_now.minute) - (target_time.hour * 60 + target_time.minute))
        if delta_minutes > 4:
            continue

        if settings_obj.last_sent_at and settings_obj.last_sent_at.astimezone(tz).date() == local_now.date():
            continue

        period_from, period_to = _default_daily_period(settings_obj.timezone)
        try:
            report_data = collect_report_data(settings_obj.client, period_from, period_to, settings_obj.timezone)
            pdf_bytes = generate_pdf_bytes(settings_obj.client, settings_obj.user, report_data)
            filename = report_filename(settings_obj.client, period_from, period_to)
            file_path = save_report_file(filename, pdf_bytes)

            delivery = deliver_report(
                settings_obj=settings_obj,
                filename=filename,
                pdf_bytes=pdf_bytes,
                period_from=period_from,
                period_to=period_to,
            )

            log_report_result(
                user=settings_obj.user,
                client=settings_obj.client,
                period_from=period_from,
                period_to=period_to,
                status=delivery["status"],
                trigger_type=ReportLog.TriggerType.SCHEDULED,
                file_path=file_path,
                delivery_channels=delivery["channels_label"],
                error=delivery["error_text"],
            )

            settings_obj.last_sent_at = timezone.now()
            settings_obj.last_status = ReportSettings.LastStatus.SUCCESS if delivery["status"] == ReportLog.Status.SUCCESS else ReportSettings.LastStatus.ERROR
            settings_obj.last_error = delivery["error_text"]
            settings_obj.save(update_fields=["last_sent_at", "last_status", "last_error", "updated_at"])
            processed += 1
            logger.info(
                "reports.daily sent: client_id=%s user_id=%s status=%s channels=%s period=%s..%s",
                settings_obj.client_id,
                settings_obj.user_id,
                delivery["status"],
                delivery["channels_label"],
                period_from,
                period_to,
            )
        except Exception as exc:
            logger.exception("reports.daily failed client_id=%s user_id=%s", settings_obj.client_id, settings_obj.user_id)
            settings_obj.last_status = ReportSettings.LastStatus.ERROR
            settings_obj.last_error = str(exc)
            settings_obj.save(update_fields=["last_status", "last_error", "updated_at"])

    return processed
