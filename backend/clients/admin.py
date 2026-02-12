from clients.models import Client
from django.contrib import admin
from django.utils.html import format_html


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "uuid", "owner", "is_active", "send_to_telegram", "created_at")
    search_fields = ("name", "owner__email", "api_key")
    list_filter = ("is_active", "created_at")
    ordering = ("-created_at",)

    readonly_fields = ("uuid", "api_key", "public_script_snippet")

    fieldsets = (
        (None, {
            "fields": (
                "owner",
                "name",
                "uuid",
                "api_key",
                "public_script_snippet",
                "telegram_chat_id",
                "send_to_telegram",
                "is_active",
            )
        }),
    )

    def public_script_snippet(self, obj):
        if not obj.pk:
            return "-"
        return format_html("<code>{}</code>", obj.public_script_tag)

    public_script_snippet.short_description = "Публичный скрипт подключения"
