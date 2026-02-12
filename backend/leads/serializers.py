from rest_framework import serializers

from leads.models import Lead
from leads.tasks import send_lead_notification_task
from leads.utils import normalize_phone


class PublicLeadCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False, allow_blank=True, label="Name")
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True, label="Phone")
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True, label="Email")

    class Meta:
        model = Lead
        fields = (
            "name",
            "phone",
            "email",
            "message",
            "source_url",
            "utm_source",
            "utm_medium",
            "utm_campaign",
        )

    def validate(self, attrs):
        name = (attrs.get("name") or "").strip()
        attrs["name"] = name

        raw_email = attrs.get("email")
        if raw_email is not None:
            email = str(raw_email).strip().lower()
            attrs["email"] = email or None

        attrs["phone"] = normalize_phone(attrs.get("phone"))
        return attrs

    def create(self, validated_data):
        client = self.context["client"]
        validated_data.setdefault("name", "")
        lead = Lead.objects.create(client=client, status=Lead.Status.NEW, **validated_data)
        send_lead_notification_task.delay(lead.id)
        return lead


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = (
            "id",
            "name",
            "phone",
            "email",
            "message",
            "source_url",
            "utm_source",
            "utm_medium",
            "utm_campaign",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class LeadStatusSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=Lead.Status.choices, label="Status")

    class Meta:
        model = Lead
        fields = ("status",)
