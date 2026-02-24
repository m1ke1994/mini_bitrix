from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.views import ChangePasswordView, LoginView, LogoutView, RegisterView
from analytics_app.views import (
    AnalyticsDevicesView,
    AnalyticsEngagementView,
    AnalyticsOverviewView,
    AnalyticsSummaryView,
    AnalyticsUniqueDailyView,
    PublicAnalyticsEventCreateView,
    PublicEventCreateView,
)
from clients.views import ClientSettingsView, tracker_js_view
from leads.views import LeadViewSet, PublicLeadCreateView
from rest_framework.routers import DefaultRouter
from subscriptions.views import YooKassaWebhookView
from telegram_logs.views import TelegramWebhookView

router = DefaultRouter()
router.register("leads", LeadViewSet, basename="lead")

admin.site.site_header = "SaaS-платформа управления заявками"
admin.site.site_title = "Администрирование SaaS"
admin.site.index_title = "Панель управления"

urlpatterns = [
    path("tracker.js", tracker_js_view, name="tracker_js"),
    path("api/track/", include("tracker.urls")),
    path("admin/", admin.site.urls),
    path("api/auth/register/", RegisterView.as_view(), name="register"),
    path("api/auth/login/", LoginView.as_view(), name="login"),
    path("api/auth/logout/", LogoutView.as_view(), name="logout"),
    path("api/auth/change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/public/lead/", PublicLeadCreateView.as_view(), name="public_lead"),
    path("api/public/event/", PublicEventCreateView.as_view(), name="public_event"),
    path("api/analytics/event/", PublicAnalyticsEventCreateView.as_view(), name="analytics_event"),
    path("api/public/telegram/webhook/", TelegramWebhookView.as_view(), name="telegram_webhook"),
    path("api/subscriptions/yookassa/webhook/", YooKassaWebhookView.as_view(), name="yookassa_webhook_subscriptions"),
    path("api/payments/yookassa/webhook/", YooKassaWebhookView.as_view(), name="yookassa_webhook"),
    path("api/analytics/overview/", AnalyticsOverviewView.as_view(), name="analytics_overview"),
    path("api/analytics/engagement/", AnalyticsEngagementView.as_view(), name="analytics_engagement"),
    path("api/analytics/devices/", AnalyticsDevicesView.as_view(), name="analytics_devices"),
    path("api/analytics/unique-daily/", AnalyticsUniqueDailyView.as_view(), name="analytics_unique_daily"),
    path("api/analytics/summary/", AnalyticsSummaryView.as_view(), name="analytics_summary"),
    path("api/reports/", include("reports.urls")),
    path("api/subscription/", include("subscriptions.urls")),
    path("api/settings/", ClientSettingsView.as_view(), name="settings"),
    path("api/client/settings/", ClientSettingsView.as_view(), name="client_settings"),
    path("api/", include(router.urls)),
]

handler404 = "core.views.custom_404"
