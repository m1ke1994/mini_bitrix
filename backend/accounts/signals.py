from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import ClientUser
from clients.models import Client


def _client_name_for_user(user) -> str:
    email = (user.email or "").strip()
    if email:
        return email
    username = (getattr(user, "username", "") or "").strip()
    if username:
        return username
    return f"Client {user.pk}"


def _client_user_email_for_user(user) -> str:
    email = (user.email or "").strip().lower()
    if not email:
        username = (getattr(user, "username", "") or "").strip().lower()
        if "@" in username:
            email = username
        elif username:
            email = f"{username}@local.invalid"
        else:
            email = f"user-{user.pk}@local.invalid"

    exists_qs = ClientUser.objects.filter(email=email).exclude(user=user)
    if not exists_qs.exists():
        return email

    local, sep, domain = email.partition("@")
    if not sep:
        local = email
        domain = "local.invalid"
    return f"{local}+{user.pk}@{domain}"


@receiver(post_save, sender=get_user_model(), dispatch_uid="accounts.ensure_client_integration")
def ensure_client_integration(sender, instance, **kwargs):
    # Admin/staff users are not client accounts.
    if instance.is_staff or instance.is_superuser:
        return

    client, _created = Client.objects.get_or_create(
        owner=instance,
        defaults={
            "name": _client_name_for_user(instance),
            "send_to_telegram": False,
            "telegram_chat_id": None,
            "is_active": True,
        },
    )

    # Backfill token for legacy clients without api_key.
    if not client.api_key:
        client.save()

    client_user_email = _client_user_email_for_user(instance)
    client_user, _created = ClientUser.objects.get_or_create(
        user=instance,
        defaults={
            "client": client,
            "email": client_user_email,
            "is_active": True,
        },
    )

    fields_to_update = []
    if client_user.client_id != client.id:
        client_user.client = client
        fields_to_update.append("client")
    if client_user.email != client_user_email:
        client_user.email = client_user_email
        fields_to_update.append("email")
    if fields_to_update:
        client_user.save(update_fields=fields_to_update)
