from django.contrib import admin

from leads.models import Lead, LeadActivity, Pipeline, PipelineStage, Tag, WidgetVariant


class PipelineStageInline(admin.TabularInline):
    model = PipelineStage
    extra = 0
    fields = ("name", "order", "color", "is_active", "is_closed_stage", "auto_action")
    ordering = ("order", "id")


@admin.register(Pipeline)
class PipelineAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "name", "is_default", "created_at")
    list_filter = ("is_default", "created_at")
    search_fields = ("name", "client__name")
    inlines = [PipelineStageInline]


@admin.register(PipelineStage)
class PipelineStageAdmin(admin.ModelAdmin):
    list_display = ("id", "pipeline", "name", "order", "is_active", "is_closed_stage")
    list_filter = ("is_active", "is_closed_stage", "pipeline__client")
    search_fields = ("name", "pipeline__name", "pipeline__client__name")
    ordering = ("pipeline_id", "order", "id")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "name", "color", "created_at")
    list_filter = ("client", "created_at")
    search_fields = ("name", "client__name")


@admin.register(WidgetVariant)
class WidgetVariantAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "name", "is_active", "impressions", "conversions", "conversion_rate")
    list_filter = ("client", "is_active", "created_at")
    search_fields = ("name", "client__name")
    readonly_fields = ("impressions", "conversions")


class LeadActivityInline(admin.TabularInline):
    model = LeadActivity
    extra = 0
    fields = ("action_type", "description", "created_by", "created_at", "metadata")
    readonly_fields = ("created_at",)
    ordering = ("-created_at", "-id")


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "client",
        "name",
        "phone",
        "email",
        "stage",
        "status",
        "score",
        "assigned_to",
        "next_contact_at",
        "created_at",
    )
    search_fields = ("name", "phone", "email", "client__name", "assigned_to__email")
    list_filter = ("status", "stage", "client", "assigned_to", "created_at")
    ordering = ("-created_at",)
    autocomplete_fields = ("stage", "assigned_to", "tags")
    inlines = [LeadActivityInline]


@admin.register(LeadActivity)
class LeadActivityAdmin(admin.ModelAdmin):
    list_display = ("id", "lead", "action_type", "created_by", "created_at")
    list_filter = ("action_type", "created_at")
    search_fields = ("lead__id", "lead__name", "description", "created_by__email")
    readonly_fields = ("created_at",)

