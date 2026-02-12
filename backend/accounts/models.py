from django.conf import settings
from django.db import models

from clients.models import Client


class ClientUser(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_user",
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="users",
    )
    email = models.EmailField(unique=True, db_index=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Client user"
        verbose_name_plural = "Client users"

    def __str__(self) -> str:
        return f"{self.email} ({self.client.name})"
