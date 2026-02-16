from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsClientUser
from reports.models import ReportSettings
from reports.serializers import DailyToggleSerializer
from reports.services.pdf_generator import build_pdf_for_client
from reports.services.telegram_sender import send_pdf_to_client_telegram


class ReportSendNowView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientUser]

    def post(self, request):
        client = request.client
        pdf_bytes, filename = build_pdf_for_client(client=client, user=request.user)
        send_pdf_to_client_telegram(client=client, filename=filename, pdf_bytes=pdf_bytes)

        settings_obj, _ = ReportSettings.objects.get_or_create(client=client)
        settings_obj.last_sent_at = timezone.now()
        settings_obj.last_error = ""
        settings_obj.save(update_fields=["last_sent_at", "last_error", "updated_at"])
        return Response({"ok": True, "detail": "PDF отправлен в Telegram."}, status=status.HTTP_200_OK)


class ReportToggleDailyView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientUser]

    def get(self, request):
        settings_obj, _ = ReportSettings.objects.get_or_create(client=request.client)
        return Response(
            {"daily_pdf_enabled": settings_obj.daily_pdf_enabled},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = DailyToggleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        settings_obj, _ = ReportSettings.objects.get_or_create(client=request.client)
        settings_obj.daily_pdf_enabled = serializer.validated_data["enabled"]
        settings_obj.save(update_fields=["daily_pdf_enabled", "updated_at"])

        return Response(
            {"ok": True, "daily_pdf_enabled": settings_obj.daily_pdf_enabled},
            status=status.HTTP_200_OK,
        )
