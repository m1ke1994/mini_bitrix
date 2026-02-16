import logging

from django.http import HttpResponse
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsClientUser
from reports.models import ReportLog, ReportSettings
from reports.serializers import ReportGenerateSerializer, ReportLogSerializer, ReportSettingsSerializer
from reports.services import (
    _default_manual_period,
    collect_report_data,
    create_telegram_link_token,
    deliver_report,
    disconnect_telegram,
    generate_pdf_bytes,
    get_or_create_settings,
    log_report_result,
    report_filename,
    save_report_file,
)

logger = logging.getLogger(__name__)


class ReportSettingsView(generics.RetrieveUpdateAPIView):
    serializer_class = ReportSettingsSerializer
    permission_classes = [permissions.IsAuthenticated, IsClientUser]

    def get_object(self):
        return get_or_create_settings(self.request.user, self.request.client)


class ReportLatestLogView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientUser]

    def get(self, request):
        latest = ReportLog.objects.filter(client=request.client).order_by("-created_at").first()
        if not latest:
            return Response({"detail": "No logs yet."}, status=status.HTTP_200_OK)
        return Response(ReportLogSerializer(latest).data)


class ReportTelegramConnectStartView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientUser]

    def post(self, request):
        settings_obj = get_or_create_settings(request.user, request.client)
        token, bot_link = create_telegram_link_token(user=request.user, client=request.client)
        command = f"/link {token.code}"
        logger.info(
            "reports.telegram.connect start user_id=%s client_id=%s code=%s expires_at=%s",
            request.user.id,
            request.client.id,
            token.code,
            token.expires_at,
        )
        return Response(
            {
                "code": token.code,
                "command": command,
                "expires_at": token.expires_at,
                "bot_link": bot_link,
                "instruction": "Откройте бота, нажмите Start и отправьте команду /link CODE.",
                "telegram_is_connected": settings_obj.telegram_is_connected,
            }
        )


class ReportTelegramDisconnectView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientUser]

    def post(self, request):
        settings_obj = get_or_create_settings(request.user, request.client)
        disconnect_telegram(settings_obj)
        logger.info("reports.telegram.disconnect user_id=%s client_id=%s", request.user.id, request.client.id)
        return Response({"ok": True})


class ReportGenerateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientUser]

    def post(self, request):
        serializer = ReportGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        settings_obj = get_or_create_settings(request.user, request.client)
        period_from = serializer.validated_data.get("period_from")
        period_to = serializer.validated_data.get("period_to")
        if not period_from or not period_to:
            period_from, period_to = _default_manual_period()

        try:
            report_data = collect_report_data(request.client, period_from, period_to, settings_obj.timezone)
            pdf_bytes = generate_pdf_bytes(request.client, request.user, report_data)
            filename = report_filename(request.client, period_from, period_to)
            file_path = save_report_file(filename, pdf_bytes)

            delivery = deliver_report(
                settings_obj=settings_obj,
                filename=filename,
                pdf_bytes=pdf_bytes,
                period_from=period_from,
                period_to=period_to,
            )

            log_row = log_report_result(
                user=request.user,
                client=request.client,
                period_from=period_from,
                period_to=period_to,
                status=delivery["status"],
                trigger_type=ReportLog.TriggerType.MANUAL,
                file_path=file_path,
                delivery_channels=delivery["channels_label"],
                error=delivery["error_text"],
            )

            settings_obj.last_sent_at = timezone.now()
            settings_obj.last_status = ReportSettings.LastStatus.SUCCESS if delivery["status"] == ReportLog.Status.SUCCESS else ReportSettings.LastStatus.ERROR
            settings_obj.last_error = delivery["error_text"]
            settings_obj.save(update_fields=["last_sent_at", "last_status", "last_error", "updated_at"])

            logger.info(
                "reports.generate client_id=%s user_id=%s period=%s..%s status=%s channels=%s log_id=%s",
                request.client.id,
                request.user.id,
                period_from,
                period_to,
                delivery["status"],
                delivery["channels_label"],
                log_row.id,
            )

            response = HttpResponse(pdf_bytes, content_type="application/pdf")
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            response["X-Report-Log-Id"] = str(log_row.id)
            response["X-Report-Delivery-Status"] = delivery["status"]
            response["X-Report-Delivery-Channels"] = delivery["channels_label"]
            return response
        except Exception as exc:
            logger.exception("reports.generate failed client_id=%s user_id=%s", request.client.id, request.user.id)
            log_report_result(
                user=request.user,
                client=request.client,
                period_from=period_from,
                period_to=period_to,
                status=ReportLog.Status.ERROR,
                trigger_type=ReportLog.TriggerType.MANUAL,
                error=str(exc),
            )
            settings_obj.last_status = ReportSettings.LastStatus.ERROR
            settings_obj.last_error = str(exc)
            settings_obj.save(update_fields=["last_status", "last_error", "updated_at"])
            return Response({"detail": "Failed to generate report."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
