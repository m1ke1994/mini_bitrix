from rest_framework import serializers

from leads.crm import add_lead_note, schedule_lead_contact
from leads.models import Lead, LeadActivity, Pipeline, PipelineStage, Tag, WidgetVariant
from leads.services import process_public_lead_submission
from leads.utils import normalize_email, normalize_phone, normalize_phone_for_dedup


class PublicLeadCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False, allow_blank=True, label="Name")
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True, label="Phone")
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True, label="Email")
    session_id = serializers.CharField(required=False, allow_blank=True, write_only=True)
    visitor_id = serializers.CharField(required=False, allow_blank=True, write_only=True)
    variant_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)

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
            "session_id",
            "visitor_id",
            "variant_id",
        )

    def validate(self, attrs):
        name = (attrs.get("name") or "").strip()
        attrs["name"] = name

        attrs["phone"] = normalize_phone(attrs.get("phone"))
        attrs["normalized_phone"] = normalize_phone_for_dedup(attrs.get("phone"))

        raw_email = attrs.get("email")
        attrs["normalized_email"] = normalize_email(raw_email)
        attrs["email"] = attrs["normalized_email"] or None
        return attrs

    def create(self, validated_data):
        client = self.context["client"]
        session_id = (validated_data.pop("session_id", "") or "").strip()
        visitor_id = (validated_data.pop("visitor_id", "") or "").strip()
        variant_id = validated_data.pop("variant_id", None)
        result = process_public_lead_submission(
            client=client,
            payload=validated_data,
            session_id=session_id,
            visitor_id=visitor_id,
            variant_id=variant_id,
        )
        return result.lead


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color")


class WidgetVariantSerializer(serializers.ModelSerializer):
    conversion_rate = serializers.SerializerMethodField()

    class Meta:
        model = WidgetVariant
        fields = ("id", "name", "config", "impressions", "conversions", "conversion_rate", "is_active", "created_at", "updated_at")
        read_only_fields = ("impressions", "conversions", "conversion_rate", "created_at", "updated_at")

    def get_conversion_rate(self, obj):
        return obj.conversion_rate


class WidgetVariantImpressionSerializer(serializers.Serializer):
    variant_id = serializers.IntegerField(min_value=1)


class PipelineStageSerializer(serializers.ModelSerializer):
    leads_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = PipelineStage
        fields = ("id", "name", "order", "color", "auto_action", "is_active", "is_closed_stage", "leads_count")


class PipelineSerializer(serializers.ModelSerializer):
    stages = PipelineStageSerializer(many=True, read_only=True)

    class Meta:
        model = Pipeline
        fields = ("id", "name", "is_default", "stages")


class LeadActivitySerializer(serializers.ModelSerializer):
    created_by_email = serializers.SerializerMethodField()

    class Meta:
        model = LeadActivity
        fields = ("id", "action_type", "description", "created_by", "created_by_email", "metadata", "created_at")

    def get_created_by_email(self, obj):
        user = obj.created_by
        if not user:
            return None
        return user.email


class LeadSerializer(serializers.ModelSerializer):
    stage_name = serializers.SerializerMethodField()
    stage_color = serializers.SerializerMethodField()
    stage_order = serializers.SerializerMethodField()
    assigned_to_email = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)

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
            "session_id",
            "visitor_id",
            "status",
            "stage",
            "stage_name",
            "stage_color",
            "stage_order",
            "score",
            "assigned_to",
            "assigned_to_email",
            "next_contact_at",
            "last_activity_at",
            "estimated_value",
            "tags",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "last_activity_at")

    def get_stage_name(self, obj):
        return obj.stage.name if obj.stage_id else None

    def get_stage_color(self, obj):
        return obj.stage.color if obj.stage_id else None

    def get_stage_order(self, obj):
        return obj.stage.order if obj.stage_id else None

    def get_assigned_to_email(self, obj):
        if obj.assigned_to_id and obj.assigned_to:
            return obj.assigned_to.email
        return None


class LeadStatusSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=Lead.Status.choices, label="Status")

    class Meta:
        model = Lead
        fields = ("status",)


class LeadMoveSerializer(serializers.Serializer):
    stage_id = serializers.IntegerField(min_value=1)

    def validate_stage_id(self, value):
        request = self.context["request"]
        stage = PipelineStage.objects.filter(
            id=value,
            pipeline__client=request.client,
            is_active=True,
        ).select_related("pipeline").first()
        if not stage:
            raise serializers.ValidationError("Стадия не найдена.")
        self.context["target_stage"] = stage
        return value


class LeadNoteSerializer(serializers.Serializer):
    note = serializers.CharField(max_length=3000)

    def create(self, validated_data):
        lead = self.context["lead"]
        request = self.context["request"]
        note = (validated_data.get("note") or "").strip()
        return add_lead_note(
            lead,
            note=note,
            created_by=request.user if request.user.is_authenticated else None,
            metadata={"source": "crm_note"},
        )


class LeadScheduleSerializer(serializers.Serializer):
    next_contact_at = serializers.DateTimeField()
    note = serializers.CharField(required=False, allow_blank=True, max_length=1000)

    def validate_next_contact_at(self, value):
        return value

    def create(self, validated_data):
        lead = self.context["lead"]
        request = self.context["request"]
        note = (validated_data.get("note") or "").strip()
        schedule_lead_contact(
            lead,
            next_contact_at=validated_data["next_contact_at"],
            created_by=request.user if request.user.is_authenticated else None,
            description=note,
            metadata={"source": "crm_schedule"},
        )
        return lead
