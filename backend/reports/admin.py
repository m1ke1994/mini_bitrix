from django.contrib import admin

from reports.models import ReportLog, ReportSettings, TelegramLinkToken


@admin.register(ReportSettings)
class ReportSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "client",
        "user",
        "enabled",
        "send_email",
        "email_to",
        "send_telegram",
        "telegram_is_connected",
        "telegram_chat_id",
        "daily_time",
        "timezone",
        "last_sent_at",
        "last_status",
    )
    search_fields = ("client__name", "user__email", "timezone", "email_to", "telegram_chat_id", "telegram_username")
    list_filter = ("enabled", "send_email", "send_telegram", "telegram_is_connected", "last_status", "timezone")


@admin.register(ReportLog)
class ReportLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "client",
        "user",
        "period_from",
        "period_to",
        "status",
        "trigger_type",
        "delivery_channels",
        "created_at",
    )
    search_fields = ("client__name", "user__email", "file_path", "error", "delivery_channels")
    list_filter = ("status", "trigger_type", "created_at")


@admin.register(TelegramLinkToken)
class TelegramLinkTokenAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "user", "code", "expires_at", "is_used", "created_at")
    search_fields = ("code", "client__name", "user__email")
    list_filter = ("is_used", "expires_at", "created_at")
