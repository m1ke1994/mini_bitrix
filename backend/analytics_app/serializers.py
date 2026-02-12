from rest_framework import serializers

from analytics_app.models import Event


class PublicEventCreateSerializer(serializers.ModelSerializer):
    source_url = serializers.URLField(required=False, allow_null=True, allow_blank=True, write_only=True)
    utm_source = serializers.CharField(required=False, allow_null=True, allow_blank=True, write_only=True)
    utm_medium = serializers.CharField(required=False, allow_null=True, allow_blank=True, write_only=True)
    utm_campaign = serializers.CharField(required=False, allow_null=True, allow_blank=True, write_only=True)

    class Meta:
        model = Event
        fields = ("event_type", "element_id", "page_url", "source_url", "utm_source", "utm_medium", "utm_campaign")

    def create(self, validated_data):
        client = self.context["client"]
        validated_data.pop("source_url", None)
        validated_data.pop("utm_source", None)
        validated_data.pop("utm_medium", None)
        validated_data.pop("utm_campaign", None)
        return Event.objects.create(client=client, **validated_data)
