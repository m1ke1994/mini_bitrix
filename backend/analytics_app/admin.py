from analytics_app.models import Event
from django.contrib import admin


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "event_type", "page_url", "created_at")
    list_filter = ("event_type", "created_at")
    search_fields = ("page_url", "element_id", "client__name")
    ordering = ("-created_at",)
