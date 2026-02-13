from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.views import LoginView, LogoutView, RegisterView
from analytics_app.views import AnalyticsSummaryView, PublicAnalyticsEventCreateView, PublicEventCreateView, PublicVisitTrackView
from clients.views import ClientSettingsView, tracker_js_view
from leads.views import LeadViewSet, PublicLeadCreateView
from rest_framework.routers import DefaultRouter
from telegram_logs.views import TelegramWebhookView

router = DefaultRouter()
router.register("leads", LeadViewSet, basename="lead")

admin.site.site_header = "SaaS-платформа управления заявками"
admin.site.site_title = "Администрирование SaaS"
admin.site.index_title = "Панель управления"

urlpatterns = [
    path("tracker.js", tracker_js_view, name="tracker_js"),
    path("admin/", admin.site.urls),
    path("api/auth/register/", RegisterView.as_view(), name="register"),
    path("api/auth/login/", LoginView.as_view(), name="login"),
    path("api/auth/logout/", LogoutView.as_view(), name="logout"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/public/lead/", PublicLeadCreateView.as_view(), name="public_lead"),
    path("api/public/event/", PublicEventCreateView.as_view(), name="public_event"),
    path("api/track/visit/", PublicVisitTrackView.as_view(), name="track_visit"),
    path("api/analytics/event/", PublicAnalyticsEventCreateView.as_view(), name="analytics_event"),
    path("api/public/telegram/webhook/", TelegramWebhookView.as_view(), name="telegram_webhook"),
    path("api/analytics/summary/", AnalyticsSummaryView.as_view(), name="analytics_summary"),
    path("api/client/settings/", ClientSettingsView.as_view(), name="client_settings"),
    path("api/", include(router.urls)),
]
