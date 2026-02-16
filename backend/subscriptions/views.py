import logging

from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsClientUser
from subscriptions.models import Subscription, SubscriptionPayment, SubscriptionPlan
from subscriptions.serializers import CreatePaymentSerializer, SubscriptionPlanSerializer
from subscriptions.services import (
    activate_subscription_from_payment,
    create_yookassa_payment,
    notify_subscription_activated,
)

logger = logging.getLogger(__name__)


def _extract_event_type(payload: dict) -> str:
    return (
        payload.get("event")
        or payload.get("type")
        or payload.get("event_type")
        or ""
    )


def _extract_payment_object(payload: dict) -> dict:
    if isinstance(payload.get("data"), dict) and isinstance(payload.get("data", {}).get("object"), dict):
        return payload.get("data", {}).get("object")
    if isinstance(payload.get("object"), dict):
        return payload.get("object")
    return payload if isinstance(payload, dict) else {}


def _extract_metadata(payment_object: dict) -> dict:
    metadata = payment_object.get("metadata") if isinstance(payment_object, dict) else None
    return metadata if isinstance(metadata, dict) else {}


class SubscriptionStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        client = getattr(request.user, "client", None)
        if client is None:
            return Response(
                {
                    "status": Subscription.Status.EXPIRED,
                    "client_id": None,
                    "paid_until": None,
                    "is_trial": False,
                },
                status=status.HTTP_200_OK,
            )

        subscription = Subscription.objects.filter(client=client).first()
        if not subscription:
            subscription = Subscription.objects.create(
                client=client,
                status=Subscription.Status.EXPIRED,
                paid_until=None,
                is_trial=False,
                auto_renew=True,
            )

        if (
            subscription.status == Subscription.Status.ACTIVE
            and subscription.paid_until
            and subscription.paid_until <= timezone.now()
        ):
            subscription.status = Subscription.Status.EXPIRED
            subscription.save(update_fields=["status", "updated_at"])

        return Response(
            {
                "status": subscription.status,
                "client_id": client.id,
                "paid_until": subscription.paid_until,
                "is_trial": subscription.is_trial,
            },
            status=status.HTTP_200_OK,
        )


class SubscriptionPlansView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def get(self, request):
        plans = SubscriptionPlan.objects.filter(is_active=True).order_by("price")
        return Response(SubscriptionPlanSerializer(plans, many=True).data, status=status.HTTP_200_OK)


class SubscriptionCreatePaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientUser]

    def post(self, request):
        serializer = CreatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        plan = SubscriptionPlan.objects.filter(id=serializer.validated_data["plan_id"], is_active=True).first()
        if plan is None:
            return Response({"detail": "Тариф не найден."}, status=status.HTTP_404_NOT_FOUND)

        payment_data = create_yookassa_payment(client=request.client, plan=plan)
        payment = payment_data["payment"]

        return Response(
            {
                "ok": True,
                "plan": SubscriptionPlanSerializer(plan).data,
                "payment_id": payment.id,
                "yookassa_payment_id": payment.yookassa_payment_id,
                "metadata": payment_data["metadata"],
                "checkout_url": payment_data["checkout_url"],
                "confirmation_url": payment_data["confirmation_url"],
            },
            status=status.HTTP_200_OK,
        )


class SubscriptionWebhookView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        payload = request.data if isinstance(request.data, dict) else {}
        event_type = _extract_event_type(payload)
        if event_type != "payment.succeeded":
            return Response({"ok": True, "ignored": True}, status=status.HTTP_200_OK)

        payment_object = _extract_payment_object(payload)
        metadata = _extract_metadata(payment_object)
        client_id = metadata.get("client_id")
        plan_id = metadata.get("plan_id")
        local_payment_id = metadata.get("payment_id")
        yookassa_payment_id = payment_object.get("id")

        if not client_id or not plan_id:
            logger.warning("subscription webhook missing metadata: %s", payload)
            return Response({"detail": "Invalid metadata"}, status=status.HTTP_400_BAD_REQUEST)

        plan = SubscriptionPlan.objects.filter(id=plan_id, is_active=True).first()
        if plan is None:
            return Response({"detail": "Plan not found"}, status=status.HTTP_404_NOT_FOUND)

        payment = None
        if local_payment_id:
            payment = SubscriptionPayment.objects.filter(id=local_payment_id, client_id=client_id).first()
        if payment is None and yookassa_payment_id:
            payment = SubscriptionPayment.objects.filter(yookassa_payment_id=yookassa_payment_id, client_id=client_id).first()

        if payment is None:
            payment = SubscriptionPayment.objects.create(
                client_id=client_id,
                plan=plan,
                yookassa_payment_id=yookassa_payment_id or f"external-{timezone.now().timestamp()}",
                status=SubscriptionPayment.Status.SUCCEEDED,
                raw_payload=payment_object,
            )
        else:
            payment.plan = plan
            if yookassa_payment_id:
                payment.yookassa_payment_id = yookassa_payment_id
            payment.status = SubscriptionPayment.Status.SUCCEEDED
            payment.raw_payload = payment_object
            payment.save(update_fields=["plan", "yookassa_payment_id", "status", "raw_payload", "updated_at"])

        was_activated = bool(payment.activated_at)
        subscription = activate_subscription_from_payment(payment)
        if not was_activated and subscription.plan and subscription.paid_until:
            notify_subscription_activated(client=subscription.client, plan=subscription.plan, paid_until=subscription.paid_until)

        return Response(
            {
                "ok": True,
                "status": subscription.status,
                "paid_until": subscription.paid_until,
                "plan": subscription.plan_id,
            },
            status=status.HTTP_200_OK,
        )
