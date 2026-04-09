from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.views import ChangePasswordView, LoginView, LogoutView, RegisterView
from core.views import health_view
from analytics_app.views import (
    AnalyticsAiRecommendationsView,
    AnalyticsAiAdvisorView,
    AnalyticsConversionRateView,
    AnalyticsDevicesView,
    AnalyticsEngagementView,
    AnalyticsFunnelView,
    AnalyticsHeatmapView,
    AnalyticsOverviewView,
    AnalyticsResponseTimeView,
    AnalyticsSourcesView,
    AnalyticsSummaryView,
    AnalyticsTimelineView,
    AnalyticsUniqueDailyView,
    PublicAnalyticsEventCreateView,
    PublicEventCreateView,
)
from clients.views import ClientSettingsView, tracker_js_view, widget_js_view
from leads.views import (
    LeadViewSet,
    PipelineListView,
    PublicLeadCreateView,
    PublicWidgetVariantImpressionView,
    PublicWidgetVariantView,
    WidgetVariantViewSet,
)
from rest_framework.routers import DefaultRouter
from subscriptions.views import YooKassaWebhookView
from telegram_logs.views import TelegramWebhookView

router = DefaultRouter()
router.register("leads", LeadViewSet, basename="lead")
router.register("widget-variants", WidgetVariantViewSet, basename="widget_variant")

admin.site.site_header = "SaaS-платформа управления заявками"
admin.site.site_title = "Администрирование SaaS"
admin.site.index_title = "Панель управления"

urlpatterns = [
    path("api/health/", health_view, name="api_health"),
    path("tracker.js", tracker_js_view, name="tracker_js"),
    path("widget.js", widget_js_view, name="widget_js"),
    path("api/track/", include("tracker.urls")),
    path("admin/", admin.site.urls),
    path("api/auth/register/", RegisterView.as_view(), name="register"),
    path("api/auth/login/", LoginView.as_view(), name="login"),
    path("api/auth/logout/", LogoutView.as_view(), name="logout"),
    path("api/auth/change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/public/lead/", PublicLeadCreateView.as_view(), name="public_lead"),
    path("api/public/widget/variant/", PublicWidgetVariantView.as_view(), name="public_widget_variant"),
    path("api/public/widget/impression/", PublicWidgetVariantImpressionView.as_view(), name="public_widget_impression"),
    path("api/pipelines/", PipelineListView.as_view(), name="pipelines"),
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
    path("api/analytics/ai-recommendations/", AnalyticsAiRecommendationsView.as_view(), name="analytics_ai_recommendations"),
    path("api/analytics/ai-advisor/", AnalyticsAiAdvisorView.as_view(), name="analytics_ai_advisor"),
    path("api/analytics/funnel/", AnalyticsFunnelView.as_view(), name="analytics_funnel"),
    path("api/analytics/sources/", AnalyticsSourcesView.as_view(), name="analytics_sources"),
    path("api/analytics/timeline/", AnalyticsTimelineView.as_view(), name="analytics_timeline"),
    path("api/analytics/response-time/", AnalyticsResponseTimeView.as_view(), name="analytics_response_time"),
    path("api/analytics/conversion-rate/", AnalyticsConversionRateView.as_view(), name="analytics_conversion_rate"),
    path("api/analytics/heatmap/", AnalyticsHeatmapView.as_view(), name="analytics_heatmap"),
    path("api/seo/", include("seo_audit.urls")),
    path("api/reports/", include("reports.urls")),
    path("api/subscription/", include("subscriptions.urls")),
    path("api/settings/", ClientSettingsView.as_view(), name="settings"),
    path("api/client/settings/", ClientSettingsView.as_view(), name="client_settings"),
    path("api/", include(router.urls)),
]

handler404 = "core.views.custom_404"
