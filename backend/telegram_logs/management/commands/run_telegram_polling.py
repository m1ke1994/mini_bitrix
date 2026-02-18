import json
import logging
import time
import uuid

import requests
from django.conf import settings
from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.utils import timezone

from clients.models import Client
from subscriptions.models import Subscription, SubscriptionPayment, SubscriptionPlan, TelegramLink
from subscriptions.services import (
    activate_subscription_from_payment,
    create_yookassa_payment,
    refresh_payment_status,
)
from telegram_logs.models import TelegramUpdateLog
from telegram_logs.services import extract_message, save_telegram_update

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Run Telegram long polling and store updates in TelegramUpdateLog."

    def add_arguments(self, parser):
        parser.add_argument("--offset", type=int, default=None, help="Start polling from this update_id offset.")

    def _log_webhook_info(self, token: str) -> dict:
        endpoint = f"https://api.telegram.org/bot{token}/getWebhookInfo"
        try:
            response = requests.get(endpoint, timeout=15)
            response.raise_for_status()
            payload = response.json() if response.content else {}
            result = payload.get("result") if isinstance(payload, dict) else {}
            webhook_url = result.get("url") if isinstance(result, dict) else ""
            logger.info(
                "Telegram getWebhookInfo: ok=%s url=%r pending_update_count=%s last_error_date=%s last_error_message=%r",
                payload.get("ok") if isinstance(payload, dict) else None,
                webhook_url,
                result.get("pending_update_count") if isinstance(result, dict) else None,
                result.get("last_error_date") if isinstance(result, dict) else None,
                result.get("last_error_message") if isinstance(result, dict) else None,
            )
            return result if isinstance(result, dict) else {}
        except requests.RequestException:
            logger.exception("Failed to get Telegram webhook info before polling start.")
            return {}

    def _find_client_for_pay_payload(self, lookup_value: str) -> Client | None:
        if not lookup_value:
            return None

        if lookup_value.isdigit():
            client_id = int(lookup_value)
            qs = Client.objects.filter(id=client_id, is_active=True)
            logger.info(
                "Client lookup by id+is_active for pay payload: client_id=%s count=%s ids=%s",
                client_id,
                qs.count(),
                list(qs.values_list("id", flat=True)[:5]),
            )
            client = qs.first()
            if client is None:
                inactive_qs = Client.objects.filter(id=client_id)
                logger.info(
                    "Client lookup by id without active filter for pay payload: client_id=%s count=%s states=%s",
                    client_id,
                    inactive_qs.count(),
                    list(inactive_qs.values_list("id", "is_active")[:5]),
                )
            return client

        qs_api_key = Client.objects.filter(api_key=lookup_value, is_active=True)
        logger.info(
            "Client lookup by api_key+is_active for pay payload: key_prefix=%s count=%s ids=%s",
            lookup_value[:8],
            qs_api_key.count(),
            list(qs_api_key.values_list("id", flat=True)[:5]),
        )
        client = qs_api_key.first()
        if client is not None:
            return client

        try:
            client_uuid = uuid.UUID(lookup_value)
        except ValueError:
            return None

        qs_uuid = Client.objects.filter(uuid=client_uuid, is_active=True)
        logger.info(
            "Client lookup by uuid+is_active for pay payload: uuid=%s count=%s ids=%s",
            str(client_uuid),
            qs_uuid.count(),
            list(qs_uuid.values_list("id", flat=True)[:5]),
        )
        return qs_uuid.first()

    def _send_message(self, token: str, chat_id: int, text: str, reply_markup: dict | None = None) -> None:
        endpoint = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        if reply_markup:
            payload["reply_markup"] = reply_markup
        try:
            response = requests.post(endpoint, json=payload, timeout=15)
            response.raise_for_status()
            response_payload = response.json()
            if not response_payload.get("ok"):
                logger.warning("Telegram sendMessage not ok: chat_id=%s payload=%s", chat_id, response_payload)
        except requests.RequestException:
            logger.exception("Failed to send Telegram message to chat_id=%s", chat_id)

    def _answer_callback(self, token: str, callback_query_id: str, text: str | None = None) -> None:
        endpoint = f"https://api.telegram.org/bot{token}/answerCallbackQuery"
        payload = {"callback_query_id": callback_query_id}
        if text:
            payload["text"] = text
        try:
            response = requests.post(endpoint, json=payload, timeout=15)
            response.raise_for_status()
        except requests.RequestException:
            logger.exception("Failed to answer callback_query_id=%s", callback_query_id)

    def _send_payment_plans_keyboard(self, token: str, chat_id: int) -> None:
        plans = SubscriptionPlan.objects.filter(is_active=True).order_by("price")
        if not plans.exists():
            self._send_message(token, chat_id, "Тарифы пока не настроены. Попробуйте позже.")
            return

        inline_keyboard = []
        for plan in plans:
            inline_keyboard.append(
                [
                    {
                        "text": f"{plan.name} — {int(plan.price)} ₽",
                        "callback_data": f"plan_{plan.id}",
                    }
                ]
            )
        self._send_message(
            token,
            chat_id,
            "Выберите тариф:",
            reply_markup={"inline_keyboard": inline_keyboard},
        )

    def _send_payment_link_message(self, token: str, chat_id: int, confirmation_url: str, payment_id: int) -> None:
        self._send_message(
            token,
            chat_id,
            f"Для оплаты перейдите по ссылке:\n{confirmation_url}",
            reply_markup={
                "inline_keyboard": [
                    [
                        {
                            "text": "Проверить оплату",
                            "callback_data": f"check_payment_{payment_id}",
                        }
                    ]
                ]
            },
        )

    def _upsert_telegram_link(self, *, sender_id: int, chat_id: int, client: Client) -> TelegramLink:
        link_by_sender = TelegramLink.objects.filter(telegram_user_id=sender_id).select_related("client").first()
        link_by_client = TelegramLink.objects.filter(client=client).select_related("client").first()

        if link_by_sender and link_by_client and link_by_sender.pk != link_by_client.pk:
            logger.warning(
                "telegram link conflict resolved by sender. sender_id=%s chat_id=%s sender_client_id=%s target_client_id=%s",
                sender_id,
                chat_id,
                link_by_sender.client_id,
                client.id,
            )
            link_by_client.delete()

        link = link_by_sender or link_by_client
        if link is None:
            return TelegramLink.objects.create(
                telegram_user_id=sender_id,
                telegram_chat_id=chat_id,
                client=client,
            )

        update_fields = []
        if link.telegram_user_id != sender_id:
            link.telegram_user_id = sender_id
            update_fields.append("telegram_user_id")
        if link.telegram_chat_id != chat_id:
            link.telegram_chat_id = chat_id
            update_fields.append("telegram_chat_id")
        if link.client_id != client.id:
            link.client = client
            update_fields.append("client")
        if update_fields:
            link.save(update_fields=[*update_fields, "updated_at"])
        return link

    def _resolve_payment_link(self, *, sender_id: int, chat_id: int) -> TelegramLink | None:
        link = TelegramLink.objects.filter(telegram_user_id=sender_id).select_related("client").first()
        if link is not None:
            if link.telegram_chat_id != chat_id:
                link.telegram_chat_id = chat_id
                link.save(update_fields=["telegram_chat_id", "updated_at"])
            return link

        client = Client.objects.filter(telegram_chat_id=str(chat_id), is_active=True).first()
        if client is None:
            return None
        return self._upsert_telegram_link(sender_id=sender_id, chat_id=chat_id, client=client)

    def _handle_start_command(self, token: str, text: str | None, chat_id: int | None, sender_id: int | None) -> None:
        if not text or chat_id is None:
            return

        normalized = text.strip()
        if not normalized:
            return

        command = normalized.split(maxsplit=1)[0].lower()
        if command == "/trial":
            self._handle_trial_command(token, chat_id, sender_id)
            return
        if not command.startswith("/start"):
            return

        parts = normalized.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip():
            self._send_message(token, chat_id, "Используйте кнопку подключения из кабинета TrackNode.")
            return

        payload = parts[1].strip()
        logger.info(
            "Telegram /start payload received chat_id=%s sender_id=%s payload=%r",
            chat_id,
            sender_id,
            payload,
        )
        if payload.lower().startswith("pay_"):
            if sender_id is None:
                self._send_message(token, chat_id, "Ошибка: не удалось определить пользователя Telegram.")
                return

<<<<<<< HEAD
            client_lookup_value = payload[4:].strip()
            client = self._find_client_for_pay_payload(client_lookup_value)
            if client is None:
                self._send_message(token, chat_id, "Ошибка оплаты: неверная ссылка.")
                return

            logger.info(
                "Resolved pay payload to client: lookup_value=%r client_id=%s",
                client_lookup_value,
                client.id,
            )
=======
            client_id_raw = payload[4:].strip()
            logger.info(
                "telegram pay start received. sender_id=%s chat_id=%s client_id_raw=%r",
                sender_id,
                chat_id,
                client_id_raw,
            )
            if not client_id_raw.isdigit():
                self._send_message(token, chat_id, "Ошибка оплаты: неверная ссылка.")
                return

            client = Client.objects.filter(id=int(client_id_raw)).first()
>>>>>>> 156e2de17d2910ddb3f4c000492b8c6fe37b7f6d
            if client is None:
                logger.warning(
                    "telegram pay start client not found. sender_id=%s chat_id=%s client_id_raw=%r",
                    sender_id,
                    chat_id,
                    client_id_raw,
                )
                self._send_message(token, chat_id, "Ошибка оплаты: клиент не найден.")
                return
            if not client.is_active:
                logger.warning(
                    "telegram pay start for inactive client allowed. sender_id=%s chat_id=%s client_id=%s",
                    sender_id,
                    chat_id,
                    client.id,
                )

            self._upsert_telegram_link(sender_id=sender_id, chat_id=chat_id, client=client)

            logger.info(
                "Telegram pay link bound sender_id=%s chat_id=%s client_id=%s telegram_link_id=%s",
                sender_id,
                chat_id,
                client.id,
                link.id,
            )
            self._send_payment_plans_keyboard(token, chat_id)
            return

        api_key = payload
        client = Client.objects.filter(api_key=api_key).first()
        if client is None:
            self._send_message(token, chat_id, "Ошибка подключения. Неверная ссылка.")
            return

        previous_chat_id = client.telegram_chat_id
        client.telegram_chat_id = str(chat_id)
        client.send_to_telegram = True
        client.save(update_fields=["telegram_chat_id", "send_to_telegram"])
        logger.info(
            "telegram binding success. client_id=%s old_chat_id=%s new_chat_id=%s",
            client.id,
            previous_chat_id,
            client.telegram_chat_id,
        )
        if sender_id is not None:
            self._upsert_telegram_link(sender_id=sender_id, chat_id=chat_id, client=client)
        self._send_message(token, chat_id, "Telegram подключён к вашему кабинету TrackNode.")

    def _handle_trial_command(self, token: str, chat_id: int, sender_id: int | None) -> None:
        subscription = None

        if sender_id is not None:
            link = TelegramLink.objects.filter(telegram_user_id=sender_id).select_related("client").first()
            if link is not None:
                subscription = Subscription.objects.filter(client=link.client).first()

        if subscription is None:
            client = Client.objects.filter(telegram_chat_id=str(chat_id), is_active=True).first()
            if client is not None:
                subscription = Subscription.objects.filter(client=client).first()

        if subscription is None:
            self._send_message(token, chat_id, "Триал не найден. Подключите Telegram из кабинета TrackNode.")
            return

        if subscription.status == Subscription.Status.ACTIVE and subscription.paid_until and subscription.paid_until <= timezone.now():
            subscription.status = Subscription.Status.EXPIRED
            subscription.save(update_fields=["status", "updated_at"])

        if not subscription.is_trial or subscription.status != Subscription.Status.ACTIVE:
            self._send_message(token, chat_id, "Демо-доступ не активен.")
            return

        paid_until_text = timezone.localtime(subscription.paid_until).strftime("%d.%m.%Y %H:%M") if subscription.paid_until else "-"
        self._send_message(
            token,
            chat_id,
            f"🎁 У вас активирован демо-доступ.\nДействует до: {paid_until_text}",
        )

    def _resolve_callback_context(self, callback_query: dict) -> tuple[str | None, int | None, int | None]:
        data = callback_query.get("data") or ""
        sender = callback_query.get("from") if isinstance(callback_query.get("from"), dict) else {}
        sender_id = sender.get("id")
        message = callback_query.get("message") if isinstance(callback_query.get("message"), dict) else {}
        chat = message.get("chat") if isinstance(message.get("chat"), dict) else {}
        chat_id = chat.get("id")
        return data, sender_id, chat_id

    def _handle_plan_callback(self, token: str, sender_id: int, chat_id: int, data: str) -> None:
        plan_id_raw = data.split("_", 1)[1].strip()
        if not plan_id_raw.isdigit():
            self._send_message(token, chat_id, "Ошибка оплаты: неверный тариф.")
            return

        link = self._resolve_payment_link(sender_id=sender_id, chat_id=chat_id)
        if link is None:
            self._send_message(token, chat_id, "Ошибка оплаты: клиент не найден для текущего чата.")
            return

        plan = SubscriptionPlan.objects.filter(id=int(plan_id_raw), is_active=True).first()
        if plan is None:
            self._send_message(token, chat_id, "Тариф недоступен.")
            return

        payment_data = create_yookassa_payment(client=link.client, plan=plan)
        logger.info(
            "Telegram plan callback payment create result: client_id=%s plan_id=%s has_error=%s payment_id=%s yookassa_id=%s status=%s",
            link.client_id,
            plan.id,
            bool(payment_data.get("error")),
            getattr(payment_data.get("payment"), "id", None),
            getattr(payment_data.get("payment"), "yookassa_payment_id", None),
            getattr(payment_data.get("payment"), "status", None),
        )
        if payment_data.get("error"):
            self._send_message(
                token,
                chat_id,
                "Платёж создан, но не удалось получить ссылку подтверждения. Обратитесь к администратору.",
            )
            logger.error(
                "payment confirmation missing in telegram plan callback client_id=%s plan_id=%s error=%s status=%s raw=%s",
                link.client_id,
                plan.id,
                payment_data.get("error"),
                payment_data.get("status"),
                payment_data.get("raw"),
            )
            return
        payment = payment_data["payment"]
        confirmation_url = payment_data.get("confirmation_url") or payment_data.get("checkout_url")
        if not confirmation_url:
            self._send_message(token, chat_id, "Ошибка оплаты: ссылка недоступна. Попробуйте позже.")
            return

        self._send_payment_link_message(token, chat_id, confirmation_url, payment.id)

    def _handle_check_payment_callback(self, token: str, sender_id: int, chat_id: int, data: str) -> None:
        payment_id_raw = data.split("check_payment_", 1)[1].strip()
        if not payment_id_raw.isdigit():
            self._send_message(token, chat_id, "Ошибка: неверный идентификатор платежа.")
            return

        payment = (
            SubscriptionPayment.objects.select_related("plan", "client")
            .filter(id=int(payment_id_raw))
            .first()
        )
<<<<<<< HEAD
        logger.info(
            "Telegram check_payment lookup: requested_payment_id=%s found=%s found_client_id=%s requester_client_id=%s created_at=%s activated_at=%s",
            payment_id_raw,
            payment is not None,
            payment.client_id if payment else None,
            link.client_id,
            payment.created_at if payment else None,
            payment.activated_at if payment else None,
        )
        if payment is None or payment.client_id != link.client_id:
=======
        if payment is None:
>>>>>>> 156e2de17d2910ddb3f4c000492b8c6fe37b7f6d
            self._send_message(token, chat_id, "Платёж не найден.")
            return

        link = self._resolve_payment_link(sender_id=sender_id, chat_id=chat_id)
        if link is None:
            link = self._upsert_telegram_link(sender_id=sender_id, chat_id=chat_id, client=payment.client)
            logger.info(
                "telegram link auto-created from payment callback. sender_id=%s chat_id=%s client_id=%s payment_id=%s",
                sender_id,
                chat_id,
                payment.client_id,
                payment.id,
            )
        elif link.client_id != payment.client_id:
            logger.warning(
                "telegram link client mismatch fixed from payment callback. sender_id=%s chat_id=%s link_client_id=%s payment_client_id=%s payment_id=%s",
                sender_id,
                chat_id,
                link.client_id,
                payment.client_id,
                payment.id,
            )
            link = self._upsert_telegram_link(sender_id=sender_id, chat_id=chat_id, client=payment.client)

        try:
            provider_status = refresh_payment_status(payment)
            logger.info(
                "Telegram check_payment provider status: payment_id=%s provider_status=%s local_status=%s",
                payment.id,
                provider_status,
                payment.status,
            )
        except requests.RequestException:
            logger.exception("Failed to refresh payment status payment_id=%s", payment.id)
            self._send_message(token, chat_id, "Не удалось проверить оплату. Попробуйте позже.")
            return

        if provider_status == SubscriptionPayment.Status.SUCCEEDED:
            subscription = activate_subscription_from_payment(payment)
            paid_until_text = subscription.paid_until.strftime("%d.%m.%Y %H:%M") if subscription.paid_until else "-"
            self._send_message(token, chat_id, f"Оплата подтверждена. Подписка активна до {paid_until_text}.")
            return

        if provider_status == SubscriptionPayment.Status.CANCELED:
            self._send_message(token, chat_id, "Платёж отменён.")
            return

        self._send_message(token, chat_id, "Платёж ещё обрабатывается.")

    def _handle_renew_now_callback(self, token: str, sender_id: int, chat_id: int, data: str) -> None:
        subscription_id_raw = data.split("renew_now_", 1)[1].strip()
        if not subscription_id_raw.isdigit():
            self._send_message(token, chat_id, "Ошибка: неверные параметры продления.")
            return

        link = self._resolve_payment_link(sender_id=sender_id, chat_id=chat_id)
        if link is None:
            self._send_message(token, chat_id, "Ошибка оплаты: клиент не найден для текущего чата.")
            return

        subscription = (
            Subscription.objects.select_related("plan")
            .filter(id=int(subscription_id_raw), client_id=link.client_id)
            .first()
        )
        if subscription is None:
            self._send_message(token, chat_id, "Подписка не найдена.")
            return
        if subscription.plan is None or not subscription.plan.is_active:
            self._send_message(token, chat_id, "Текущий тариф недоступен для продления.")
            return

        payment_data = create_yookassa_payment(client=link.client, plan=subscription.plan)
        logger.info(
            "Telegram renew callback payment create result: client_id=%s subscription_id=%s plan_id=%s has_error=%s payment_id=%s yookassa_id=%s status=%s",
            link.client_id,
            subscription.id,
            subscription.plan.id if subscription.plan else None,
            bool(payment_data.get("error")),
            getattr(payment_data.get("payment"), "id", None),
            getattr(payment_data.get("payment"), "yookassa_payment_id", None),
            getattr(payment_data.get("payment"), "status", None),
        )
        if payment_data.get("error"):
            self._send_message(
                token,
                chat_id,
                "Платёж создан, но не удалось получить ссылку подтверждения. Обратитесь к администратору.",
            )
            logger.error(
                "payment confirmation missing in telegram renew callback client_id=%s subscription_id=%s error=%s status=%s raw=%s",
                link.client_id,
                subscription.id,
                payment_data.get("error"),
                payment_data.get("status"),
                payment_data.get("raw"),
            )
            return
        payment = payment_data["payment"]
        confirmation_url = payment_data.get("confirmation_url") or payment_data.get("checkout_url")
        if not confirmation_url:
            self._send_message(token, chat_id, "Ошибка оплаты: ссылка недоступна. Попробуйте позже.")
            return

        self._send_payment_link_message(token, chat_id, confirmation_url, payment.id)

    def _handle_disable_auto_renew_callback(self, token: str, sender_id: int, chat_id: int, data: str) -> None:
        subscription_id_raw = data.split("disable_auto_renew_", 1)[1].strip()
        if not subscription_id_raw.isdigit():
            self._send_message(token, chat_id, "Ошибка: неверные параметры автопродления.")
            return

        link = TelegramLink.objects.filter(telegram_user_id=sender_id).select_related("client").first()
        if link is None:
            self._send_message(token, chat_id, "Связка Telegram и кабинета не найдена.")
            return

        subscription = Subscription.objects.filter(id=int(subscription_id_raw), client_id=link.client_id).first()
        if subscription is None:
            self._send_message(token, chat_id, "Подписка не найдена.")
            return

        if not subscription.auto_renew:
            self._send_message(token, chat_id, "Автопродление уже отключено.")
            return

        subscription.auto_renew = False
        subscription.save(update_fields=["auto_renew", "updated_at"])
        self._send_message(token, chat_id, "Автопродление отключено.")

    def _handle_callback(self, token: str, callback_query: dict) -> None:
        callback_id = callback_query.get("id")
        if callback_id:
            self._answer_callback(token, callback_id)

        data, sender_id, chat_id = self._resolve_callback_context(callback_query)
        if not data or sender_id is None or chat_id is None:
            return

        if data.startswith("plan_"):
            self._handle_plan_callback(token, sender_id, chat_id, data)
            return
        if data.startswith("check_payment_"):
            self._handle_check_payment_callback(token, sender_id, chat_id, data)
            return
        if data.startswith("renew_now_"):
            self._handle_renew_now_callback(token, sender_id, chat_id, data)
            return
        if data.startswith("disable_auto_renew_"):
            self._handle_disable_auto_renew_callback(token, sender_id, chat_id, data)
            return

    def handle(self, *args, **options):
        token = settings.TELEGRAM_BOT_TOKEN
        if not token:
            logger.error("TELEGRAM_BOT_TOKEN is empty. Polling cannot start.")
            return

        timeout_seconds = int(getattr(settings, "TELEGRAM_POLLING_TIMEOUT", 30))
        sleep_seconds = float(getattr(settings, "TELEGRAM_POLLING_RETRY_DELAY", 2))
        get_updates_endpoint = f"https://api.telegram.org/bot{token}/getUpdates"
        delete_webhook_endpoint = f"https://api.telegram.org/bot{token}/deleteWebhook"
        lock_key = str(getattr(settings, "TELEGRAM_POLLING_LOCK_KEY", "telegram:polling:lock"))
        lock_ttl = int(getattr(settings, "TELEGRAM_POLLING_LOCK_TTL", 120))
        lock_value = uuid.uuid4().hex

        if not cache.add(lock_key, lock_value, timeout=lock_ttl):
            logger.error("Telegram polling lock is already held. Exiting current process. lock_key=%s", lock_key)
            return
        logger.info("Telegram polling lock acquired. lock_key=%s ttl=%s", lock_key, lock_ttl)

        webhook_info = self._log_webhook_info(token)
        webhook_url = (webhook_info.get("url") or "").strip() if isinstance(webhook_info, dict) else ""
        if webhook_url:
            try:
                response = requests.post(delete_webhook_endpoint, json={"drop_pending_updates": False}, timeout=15)
                response.raise_for_status()
                logger.info("Telegram webhook disabled for polling mode. previous_url=%r", webhook_url)
            except requests.RequestException:
                logger.exception("Failed to disable Telegram webhook before polling start.")
        else:
            logger.info("Telegram webhook is not configured. Polling can start.")
        self._log_webhook_info(token)

        offset = options.get("offset")
        if offset is None:
            latest = TelegramUpdateLog.objects.order_by("-update_id").values_list("update_id", flat=True).first()
            if latest is not None:
                offset = latest + 1

        logger.info("Telegram polling started. timeout=%s retry=%s offset=%s", timeout_seconds, sleep_seconds, offset)

        try:
            while True:
                if not cache.touch(lock_key, lock_ttl):
                    current_holder = cache.get(lock_key)
                    if current_holder != lock_value:
                        logger.error(
                            "Telegram polling lock lost. Stopping polling loop. lock_key=%s holder=%s",
                            lock_key,
                            current_holder,
                        )
                        return
                    cache.set(lock_key, lock_value, timeout=lock_ttl)

                params = {
                    "timeout": timeout_seconds,
                    "allowed_updates": ["message", "edited_message", "channel_post", "edited_channel_post", "callback_query"],
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

                            callback_query = update.get("callback_query") if isinstance(update.get("callback_query"), dict) else {}
                            callback_data = callback_query.get("data") if callback_query else None

                            logger.info(
                                "Incoming update update_id=%s chat_id=%s from_id=%s username=%s text=%r callback=%r payload=%s",
                                update_id,
                                chat.get("id"),
                                sender.get("id"),
                                sender.get("username"),
                                text,
                                callback_data,
                                json.dumps(update, ensure_ascii=False),
                            )

                            if update_id is None:
                                logger.warning("Update without update_id skipped. payload=%s", update)
                                continue

                            _, created = save_telegram_update(update)
                            if not created:
                                logger.info("Duplicate update ignored update_id=%s", update_id)

                            chat_id = chat.get("id")
                            sender_id = sender.get("id")
                            self._handle_start_command(token, text, chat_id, sender_id)
                            if callback_query:
                                self._handle_callback(token, callback_query)
                        except Exception:
                            logger.exception("Failed to process update_id=%s", update_id)
                        finally:
                            if update_id is not None:
                                offset = update_id + 1
                except requests.HTTPError as exc:
                    status_code = exc.response.status_code if exc.response is not None else None
                    if status_code == 409:
                        logger.error(
                            "Telegram polling conflict (409). Another getUpdates consumer is active or webhook conflicts."
                        )
                    else:
                        logger.exception("Telegram polling HTTP error status=%s", status_code)
                    time.sleep(sleep_seconds)
                except requests.RequestException:
                    logger.exception("Telegram polling request error.")
                    time.sleep(sleep_seconds)
                except Exception:
                    logger.exception("Unexpected polling loop error.")
                    time.sleep(sleep_seconds)
        finally:
            if cache.get(lock_key) == lock_value:
                cache.delete(lock_key)
                logger.info("Telegram polling lock released. lock_key=%s", lock_key)
