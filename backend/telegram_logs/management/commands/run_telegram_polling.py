import json
import logging
import time

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from clients.models import Client
from telegram_logs.models import TelegramUpdateLog
from telegram_logs.services import extract_message, save_telegram_update

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Run Telegram long polling and store updates in TelegramUpdateLog."

    def add_arguments(self, parser):
        parser.add_argument("--offset", type=int, default=None, help="Start polling from this update_id offset.")

    def _send_message(self, token: str, chat_id: int, text: str) -> None:
        endpoint = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            response = requests.post(endpoint, json={"chat_id": chat_id, "text": text}, timeout=15)
            response.raise_for_status()
            payload = response.json()
            if not payload.get("ok"):
                logger.warning("Telegram sendMessage not ok: chat_id=%s payload=%s", chat_id, payload)
        except requests.RequestException:
            logger.exception("Failed to send Telegram message to chat_id=%s", chat_id)

    def _handle_start_command(self, token: str, text: str | None, chat_id: int | None) -> None:
        if not text or not text.strip().lower().startswith("/start"):
            return
        if chat_id is None:
            return

        self._send_message(
            token,
            chat_id,
            "Привет! Для подключения отчётов откройте кабинет TrackNode и нажмите 'Подключить Telegram'. "
            "Затем отправьте сюда команду /link CODE.",
        )

    def _handle_legacy_start_key(self, token: str, text: str | None, chat_id: int | None) -> None:
        if not text or chat_id is None:
            return
        normalized = text.strip()
        if not normalized.lower().startswith("/start "):
            return
        parts = normalized.split(maxsplit=1)
        if len(parts) < 2:
            return

        candidate = parts[1].strip()
        client = Client.objects.filter(api_key=candidate, is_active=True).first()
        if client is None:
            return

        previous_chat_id = client.telegram_chat_id
        client.telegram_chat_id = str(chat_id)
        client.send_to_telegram = True
        client.save(update_fields=["telegram_chat_id", "send_to_telegram"])
        logger.info(
            "legacy telegram binding success. client_id=%s old_chat_id=%s new_chat_id=%s",
            client.id,
            previous_chat_id,
            client.telegram_chat_id,
        )
        self._send_message(token, chat_id, "Telegram подключен.")

    def handle(self, *args, **options):
        token = settings.TELEGRAM_BOT_TOKEN
        if not token:
            logger.error("TELEGRAM_BOT_TOKEN is empty. Polling cannot start.")
            return

        timeout_seconds = int(getattr(settings, "TELEGRAM_POLLING_TIMEOUT", 30))
        sleep_seconds = float(getattr(settings, "TELEGRAM_POLLING_RETRY_DELAY", 2))
        delete_webhook = bool(getattr(settings, "TELEGRAM_POLLING_DELETE_WEBHOOK", True))
        get_updates_endpoint = f"https://api.telegram.org/bot{token}/getUpdates"
        delete_webhook_endpoint = f"https://api.telegram.org/bot{token}/deleteWebhook"

        if delete_webhook:
            try:
                response = requests.post(delete_webhook_endpoint, json={"drop_pending_updates": False}, timeout=15)
                response.raise_for_status()
                logger.info("Telegram webhook disabled for polling mode.")
            except requests.RequestException:
                logger.exception("Failed to disable Telegram webhook before polling start.")

        offset = options.get("offset")
        if offset is None:
            latest = TelegramUpdateLog.objects.order_by("-update_id").values_list("update_id", flat=True).first()
            if latest is not None:
                offset = latest + 1

        logger.info("Telegram polling started. timeout=%s retry=%s offset=%s", timeout_seconds, sleep_seconds, offset)

        while True:
            params = {
                "timeout": timeout_seconds,
                "allowed_updates": ["message", "edited_message", "channel_post", "edited_channel_post"],
            }
            if offset is not None:
                params["offset"] = offset

            try:
                response = requests.get(get_updates_endpoint, params=params, timeout=timeout_seconds + 10)
                response.raise_for_status()
                payload = response.json()
                if not payload.get("ok"):
                    logger.warning("Telegram API non-ok payload: %s", payload)
                    time.sleep(sleep_seconds)
                    continue

                updates = payload.get("result", [])
                if updates:
                    logger.info("Received updates count=%s", len(updates))

                for update in updates:
                    update_id = update.get("update_id")
                    try:
                        message = extract_message(update)
                        chat = message.get("chat", {}) if isinstance(message, dict) else {}
                        sender = message.get("from", {}) if isinstance(message, dict) else {}
                        text = message.get("text") if isinstance(message, dict) else None
                        if not text and isinstance(message, dict):
                            text = message.get("caption")

                        logger.info(
                            "Incoming update update_id=%s chat_id=%s from_id=%s username=%s text=%r payload=%s",
                            update_id,
                            chat.get("id"),
                            sender.get("id"),
                            sender.get("username"),
                            text,
                            json.dumps(update, ensure_ascii=False),
                        )

                        if update_id is None:
                            logger.warning("Update without update_id skipped. payload=%s", update)
                            continue

                        _, created = save_telegram_update(update)
                        if not created:
                            logger.info("Duplicate update ignored update_id=%s", update_id)

                        chat_id = chat.get("id")
                        self._handle_start_command(token, text, chat_id)
                        self._handle_legacy_start_key(token, text, chat_id)
                    except Exception:
                        logger.exception("Failed to process update_id=%s", update_id)
                    finally:
                        if update_id is not None:
                            offset = update_id + 1
            except requests.RequestException:
                logger.exception("Telegram polling request error.")
                time.sleep(sleep_seconds)
            except Exception:
                logger.exception("Unexpected polling loop error.")
                time.sleep(sleep_seconds)
