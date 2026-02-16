import json
import uuid
from datetime import timedelta

import requests
from django.conf import settings
from django.utils import timezone

from subscriptions.models import Subscription, SubscriptionPayment, TelegramLink
from subscriptions.telegram import send_telegram_message


def _yookassa_credentials() -> tuple[str, str]:
    return (
        (getattr(settings, "YOOKASSA_SHOP_ID", "") or "").strip(),
        (getattr(settings, "YOOKASSA_SECRET_KEY", "") or "").strip(),
    )


def _default_return_url() -> str:
    frontend_url = (getattr(settings, "FRONTEND_URL", "") or "").strip().rstrip("/")
    if frontend_url:
        return f"{frontend_url}/dashboard"

    configured = (getattr(settings, "PAYMENT_RETURN_URL", "") or "").strip()
    if configured:
        return configured
    public_base = (getattr(settings, "PUBLIC_BASE_URL", "") or "").strip().rstrip("/")
    if public_base:
        return f"{public_base}/dashboard"
    return "http://localhost:9003/dashboard"


def _build_fallback_checkout_url(client_id: int, plan_id: int) -> str:
    checkout_base = (getattr(settings, "PAYMENT_CHECKOUT_URL", "") or "").strip()
    if not checkout_base:
        return ""
    connector = "&" if "?" in checkout_base else "?"
    return f"{checkout_base}{connector}client_id={client_id}&plan_id={plan_id}"


def create_yookassa_payment(*, client, plan, description: str | None = None) -> dict:
    metadata = {"client_id": str(client.id), "plan_id": str(plan.id)}
    shop_id, secret_key = _yookassa_credentials()
    print("YOOKASSA CONFIG:", {"account_id_set": bool(shop_id), "secret_key_set": bool(secret_key)})

    payment = SubscriptionPayment.objects.create(
        client=client,
        plan=plan,
        yookassa_payment_id=f"mock-{uuid.uuid4().hex}",
        status=SubscriptionPayment.Status.PENDING,
        raw_payload={"metadata": metadata},
    )

    # Attach internal id so webhook/status checks can map provider payload to local payment.
    metadata["payment_id"] = str(payment.id)

    if not shop_id or not secret_key:
        fallback_url = _build_fallback_checkout_url(client.id, plan.id)
        return {
            "payment": payment,
            "metadata": metadata,
            "confirmation_url": fallback_url,
            "checkout_url": fallback_url,
        }

    endpoint = "https://api.yookassa.ru/v3/payments"
    payload = {
        "amount": {"value": f"{plan.price:.2f}", "currency": plan.currency or "RUB"},
        "confirmation": {
            "type": "redirect",
            "return_url": _default_return_url(),
        },
        "capture": True,
        "description": description or f"TrackNode subscription: {plan.name}",
        "metadata": metadata,
    }

    response = requests.post(
        endpoint,
        json=payload,
        auth=(shop_id, secret_key),
        headers={"Idempotence-Key": uuid.uuid4().hex},
        timeout=30,
    )
    response.raise_for_status()
    body = response.json()

    confirmation_url = body.get("confirmation", {}).get("confirmation_url", "")
    payment.yookassa_payment_id = body.get("id") or payment.yookassa_payment_id
    payment.status = body.get("status") or SubscriptionPayment.Status.PENDING
    payment.raw_payload = body
    payment.save(update_fields=["yookassa_payment_id", "status", "raw_payload", "updated_at"])

    print("YOOKASSA RAW RESPONSE:", json.dumps(body, default=str, ensure_ascii=False))
    print("YOOKASSA STATUS:", body.get("status"))
    print("YOOKASSA CONFIRMATION:", body.get("confirmation"))

    if not confirmation_url:
        return {
            "payment": payment,
            "metadata": metadata,
            "confirmation_url": "",
            "checkout_url": "",
            "error": "no_confirmation",
            "status": body.get("status") or payment.status,
            "raw": str(body),
        }

    return {
        "payment": payment,
        "metadata": metadata,
        "confirmation_url": confirmation_url,
        "checkout_url": confirmation_url,
    }


def refresh_payment_status(payment: SubscriptionPayment) -> str:
    shop_id, secret_key = _yookassa_credentials()
    if payment.yookassa_payment_id.startswith("mock-") or not shop_id or not secret_key:
        return payment.status

    endpoint = f"https://api.yookassa.ru/v3/payments/{payment.yookassa_payment_id}"
    response = requests.get(endpoint, auth=(shop_id, secret_key), timeout=30)
    response.raise_for_status()
    body = response.json()

    status_value = body.get("status") or payment.status
    payment.status = status_value
    payment.raw_payload = body
    payment.save(update_fields=["status", "raw_payload", "updated_at"])
    return status_value


def activate_subscription_from_payment(payment: SubscriptionPayment) -> Subscription:
    subscription, _ = Subscription.objects.get_or_create(
        client=payment.client,
        defaults={"status": Subscription.Status.EXPIRED, "is_trial": False, "auto_renew": True},
    )

    if payment.activated_at:
        return subscription

    now = timezone.now()
    plan = payment.plan
    if plan is None:
        return subscription

    if subscription.paid_until and subscription.paid_until > now:
        new_paid_until = subscription.paid_until + timedelta(days=plan.duration_days)
    else:
        new_paid_until = now + timedelta(days=plan.duration_days)

    subscription.status = Subscription.Status.ACTIVE
    subscription.plan = plan
    subscription.paid_until = new_paid_until
    subscription.is_trial = False
    subscription.save(update_fields=["status", "plan", "paid_until", "is_trial", "updated_at"])

    payment.status = SubscriptionPayment.Status.SUCCEEDED
    payment.activated_at = now
    payment.save(update_fields=["status", "activated_at", "updated_at"])
    return subscription


def notify_subscription_activated(client, plan, paid_until) -> None:
    link = TelegramLink.objects.filter(client=client).first()
    if link is None:
        return

    chat_id = link.telegram_chat_id or link.telegram_user_id
    if not chat_id:
        return

    paid_until_text = timezone.localtime(paid_until).strftime("%d.%m.%Y %H:%M") if paid_until else "-"
    text = (
        "🎉 Подписка активирована!\n\n"
        f"Тариф: {plan.name}\n"
        f"Действует до: {paid_until_text}\n\n"
        "Теперь вам доступна вся аналитика TrackNode 🚀"
    )
    send_telegram_message(chat_id=chat_id, text=text)
