from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse

from subscriptions.models import Subscription, SubscriptionPayment, SubscriptionPlan, SubscriptionSettings, TelegramLink


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "currency", "duration_days", "is_active", "updated_at")
    list_filter = ("is_active", "currency")
    search_fields = ("name",)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "plan", "status", "paid_until", "updated_at")
    list_filter = ("status",)
    search_fields = ("client__name", "client__owner__email")


@admin.register(TelegramLink)
class TelegramLinkAdmin(admin.ModelAdmin):
    list_display = ("id", "telegram_user_id", "client", "updated_at")
    search_fields = ("telegram_user_id", "client__name", "client__owner__email")


@admin.register(SubscriptionPayment)
class SubscriptionPaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "plan", "yookassa_payment_id", "status", "activated_at", "updated_at")
    list_filter = ("status", "plan")
    search_fields = ("yookassa_payment_id", "client__name", "client__owner__email")


@admin.register(SubscriptionSettings)
class SubscriptionSettingsAdmin(admin.ModelAdmin):
    list_display = ("demo_enabled", "demo_days")

    def has_add_permission(self, request):
        if SubscriptionSettings.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        settings_obj = SubscriptionSettings.get_solo()
        url = reverse(
            f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change",
            args=[settings_obj.pk],
        )
        return HttpResponseRedirect(url)
