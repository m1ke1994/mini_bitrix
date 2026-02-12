from celery import shared_task
from django.utils import timezone

from leads.models import Lead
from leads.services import send_telegram_message


@shared_task
def send_lead_notification_task(lead_id: int) -> None:
    try:
        lead = Lead.objects.select_related("client").get(id=lead_id)
    except Lead.DoesNotExist:
        return

    client = lead.client
    if not client.send_to_telegram or not client.telegram_chat_id:
        return

    local_created_at = timezone.localtime(lead.created_at)
    text = (
        "New lead\n"
        f"Client: {client.name}\n"
        f"Name: {lead.name}\n"
        f"Phone: {lead.phone}\n"
        f"Email: {lead.email or '-'}\n"
        f"Message: {lead.message or '-'}\n"
        f"Source: {lead.source_url or lead.utm_source or '-'}\n"
        f"Time: {local_created_at.strftime('%Y-%m-%d %H:%M:%S %Z')}"
    )
    send_telegram_message(client.telegram_chat_id, text)
