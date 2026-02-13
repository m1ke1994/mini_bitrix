from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from accounts.forms import AdminUserChangeForm, AdminUserCreationForm
from accounts.models import ClientUser


@admin.register(ClientUser)
class ClientUserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "client", "is_active", "created_at")
    search_fields = ("email", "client__name", "user__email")
    list_filter = ("is_active", "created_at")
    ordering = ("-created_at",)


User = get_user_model()


try:
    admin.site.unregister(User)
except NotRegistered:
    pass


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = AdminUserCreationForm
    form = AdminUserChangeForm
    list_display = ("id", "username", "email", "is_staff", "is_active", "date_joined")
    search_fields = ("username", "email")
    readonly_fields = (*BaseUserAdmin.readonly_fields, "tracker_url_readonly", "script_code_readonly")

    add_fieldsets = (
        (
            "Основная информация",
            {
                "classes": ("wide",),
                "fields": ("email", "username", "password1", "password2"),
            },
        ),
    )

    fieldsets = (
        *BaseUserAdmin.fieldsets,
        (
            "Интеграция",
            {
                "fields": (
                    "tracker_url_readonly",
                    "script_code_readonly",
                )
            },
        ),
    )

    def tracker_url_readonly(self, obj):
        if not obj:
            return "-"
        client = getattr(obj, "client", None)
        if not client:
            return "-"
        return client.tracker_script_url

    tracker_url_readonly.short_description = "URL трекера"

    def script_code_readonly(self, obj):
        if not obj:
            return "-"
        client = getattr(obj, "client", None)
        if not client:
            return "-"
        return format_html(
            '<textarea rows="3" readonly style="width:100%;font-family:monospace;">{}</textarea>',
            client.public_script_tag,
        )

    script_code_readonly.short_description = "Скрипт подключения"
