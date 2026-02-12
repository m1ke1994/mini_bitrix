from django.contrib import admin

from accounts.models import ClientUser


@admin.register(ClientUser)
class ClientUserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "client", "is_active", "created_at")
    search_fields = ("email", "client__name", "user__email")
    list_filter = ("is_active", "created_at")
    ordering = ("-created_at",)
