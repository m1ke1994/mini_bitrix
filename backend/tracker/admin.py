from django.contrib import admin

from tracker.models import Event, PageView, Site, Visit


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ("id", "domain", "is_active", "created_at")
    search_fields = ("domain", "token")
    list_filter = ("is_active",)


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ("id", "site", "visitor_id", "session_id", "ip", "started_at", "ended_at", "duration")
    search_fields = ("visitor_id", "session_id", "ip", "site__domain")
    list_filter = ("site",)


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ("id", "visit", "url", "title", "timestamp")
    search_fields = ("url", "title", "visit__session_id")
    list_filter = ("visit__site",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "visit", "type", "timestamp")
    search_fields = ("type", "visit__session_id")
    list_filter = ("type", "visit__site")
