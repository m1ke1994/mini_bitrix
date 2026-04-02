from __future__ import annotations

import json
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken


class LeadUpdatesConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        token = self._extract_token()
        user = await self._get_user_from_token(token)
        if not user:
            await self.close(code=4401)
            return

        client_id = await self._get_client_id(user.id)
        if not client_id:
            await self.close(code=4403)
            return

        self.client_id = client_id
        self.group_name = f"client_{self.client_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send_json({"type": "connected", "client_id": self.client_id})

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        if str((content or {}).get("type") or "").lower() == "ping":
            await self.send_json({"type": "pong"})

    async def lead_event(self, event):
        await self.send_json(
            {
                "type": "lead_event",
                "event": event.get("event"),
                "payload": event.get("payload") or {},
                "timestamp": event.get("timestamp"),
            }
        )

    def _extract_token(self) -> str:
        query_string = (self.scope.get("query_string") or b"").decode("utf-8", errors="ignore")
        query = parse_qs(query_string)
        token = (query.get("token") or [""])[0].strip()
        if token:
            return token
        headers = dict(self.scope.get("headers") or [])
        raw_auth = (headers.get(b"authorization") or b"").decode("utf-8", errors="ignore")
        if raw_auth.lower().startswith("bearer "):
            return raw_auth[7:].strip()
        return ""

    @database_sync_to_async
    def _get_user_from_token(self, token: str):
        if not token:
            return None
        try:
            access = AccessToken(token)
            user_id = access.get("user_id")
            if not user_id:
                return None
            user_model = get_user_model()
            return user_model.objects.filter(id=user_id, is_active=True).first()
        except Exception:
            return None

    @database_sync_to_async
    def _get_client_id(self, user_id: int) -> int | None:
        user_model = get_user_model()
        user = (
            user_model.objects.select_related("client_user__client")
            .filter(id=user_id, is_active=True)
            .first()
        )
        if not user:
            return None
        client_user = getattr(user, "client_user", None)
        if not client_user or not client_user.is_active:
            return None
        return client_user.client_id

