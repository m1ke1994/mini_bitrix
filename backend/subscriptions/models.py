from django.db import models

from clients.models import Client


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="RUB")
    duration_days = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("price",)

    def __str__(self) -> str:
        return f"{self.name} ({self.price} {self.currency}, {self.duration_days}d)"


class Subscription(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "active"
        EXPIRED = "expired", "expired"

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="subscriptions")
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subscriptions",
    )
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.EXPIRED, db_index=True)
    paid_until = models.DateTimeField(null=True, blank=True)
    is_trial = models.BooleanField(default=False)
    auto_renew = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at",)
        constraints = [
            models.UniqueConstraint(fields=["client"], name="unique_subscription_per_client"),
        ]

    def __str__(self) -> str:
        return f"subscription client={self.client_id} status={self.status} paid_until={self.paid_until}"


class TelegramLink(models.Model):
    telegram_user_id = models.BigIntegerField(unique=True, db_index=True)
    telegram_chat_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="telegram_links")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at",)
        constraints = [
            models.UniqueConstraint(fields=["client"], name="unique_telegram_link_per_client"),
        ]

    def __str__(self) -> str:
        return f"telegram_user_id={self.telegram_user_id} client_id={self.client_id}"


class SubscriptionPayment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "pending"
        SUCCEEDED = "succeeded", "succeeded"
        CANCELED = "canceled", "canceled"

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="subscription_payments")
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subscription_payments",
    )
    yookassa_payment_id = models.CharField(max_length=128, unique=True, db_index=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING, db_index=True)
    activated_at = models.DateTimeField(null=True, blank=True)
    raw_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return (
            f"payment client={self.client_id} plan={self.plan_id} "
            f"yookassa_id={self.yookassa_payment_id} status={self.status}"
        )
