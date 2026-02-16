from django.urls import path

from reports.views import (
    ReportGenerateView,
    ReportLatestLogView,
    ReportSettingsView,
    ReportTelegramConnectStartView,
    ReportTelegramDisconnectView,
)

urlpatterns = [
    path("settings/", ReportSettingsView.as_view(), name="report_settings"),
    path("logs/latest/", ReportLatestLogView.as_view(), name="report_latest_log"),
    path("telegram/connect/", ReportTelegramConnectStartView.as_view(), name="report_telegram_connect"),
    path("telegram/disconnect/", ReportTelegramDisconnectView.as_view(), name="report_telegram_disconnect"),
    path("generate/", ReportGenerateView.as_view(), name="report_generate"),
]
