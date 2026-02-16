from django.conf import settings
from django.db import models
from django.utils import timezone

from clients.models import Client


class ReportSettings(models.Model):
    class LastStatus(models.TextChoices):
        IDLE = "idle", "Idle"
        SUCCESS = "success", "Success"
        ERROR = "error", "Error"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="report_settings")
    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name="report_settings")
    enabled = models.BooleanField(default=False)
    daily_time = models.TimeField(default="09:00")
    timezone = models.CharField(max_length=64, default="Europe/Moscow")
    send_email = models.BooleanField(default=True)
    email_to = models.EmailField(blank=True, null=True)
    send_telegram = models.BooleanField(default=False)
    telegram_chat_id = models.CharField(max_length=64, blank=True, null=True)
    telegram_username = models.CharField(max_length=255, blank=True, null=True)
    telegram_is_connected = models.BooleanField(default=False)
    last_sent_at = models.DateTimeField(null=True, blank=True)
    last_status = models.CharField(max_length=16, choices=LastStatus.choices, default=LastStatus.IDLE)
    last_error = models.TextField(blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at",)

    def __str__(self) -> str:
        return f"Report settings: client={self.client_id} enabled={self.enabled}"


class ReportLog(models.Model):
    class Status(models.TextChoices):
        SUCCESS = "success", "Success"
        ERROR = "error", "Error"

    class TriggerType(models.TextChoices):
        MANUAL = "manual", "Manual"
        SCHEDULED = "scheduled", "Scheduled"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="report_logs")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="report_logs")
    period_from = models.DateField()
    period_to = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=16, choices=Status.choices)
    trigger_type = models.CharField(max_length=16, choices=TriggerType.choices, default=TriggerType.MANUAL)
    file_path = models.CharField(max_length=500, blank=True, default="")
    delivery_channels = models.CharField(max_length=64, blank=True, default="")
    error = models.TextField(blank=True, default="")

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["client", "created_at"]),
            models.Index(fields=["client", "status", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"Report log #{self.pk}: client={self.client_id} status={self.status}"


class TelegramLinkToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="telegram_link_tokens")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="telegram_link_tokens")
    code = models.CharField(max_length=16, unique=True, db_index=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["code", "expires_at"]),
            models.Index(fields=["client", "created_at"]),
        ]

    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at
