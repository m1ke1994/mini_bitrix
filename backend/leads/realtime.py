from __future__ import annotations

import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone

logger = logging.getLogger(__name__)


def broadcast_lead_event(*, client_id: int, event: str, payload: dict) -> None:
    if not client_id:
        return
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    try:
        async_to_sync(channel_layer.group_send)(
            f"client_{client_id}",
            {
                "type": "lead.event",
                "event": event,
                "payload": payload or {},
                "timestamp": timezone.now().isoformat(),
            },
        )
    except Exception:
        logger.exception("Failed to broadcast lead event client_id=%s event=%s", client_id, event)
