from django.utils import timezone
from rest_framework import permissions

from subscriptions.exceptions import PaymentRequired
from subscriptions.models import Subscription


class HasActiveSubscription(permissions.BasePermission):
    message = "Подписка не активна."

    def has_permission(self, request, view):
        client = getattr(request, "client", None)
        if client is None:
            return True

        subscription, _ = Subscription.objects.get_or_create(
            client=client,
            defaults={"status": Subscription.Status.EXPIRED, "paid_until": None, "is_trial": False, "auto_renew": True},
        )
        now = timezone.now()

        if subscription.status == Subscription.Status.ACTIVE:
            if subscription.paid_until is None or subscription.paid_until <= now:
                subscription.status = Subscription.Status.EXPIRED
                subscription.save(update_fields=["status", "updated_at"])
                raise PaymentRequired()
            return True

        raise PaymentRequired()
