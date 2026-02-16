from rest_framework import serializers

from reports.models import ReportLog, ReportSettings


class ReportSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportSettings
        fields = (
            "enabled",
            "daily_time",
            "timezone",
            "send_email",
            "email_to",
            "send_telegram",
            "telegram_chat_id",
            "telegram_username",
            "telegram_is_connected",
            "last_sent_at",
            "last_status",
            "last_error",
        )
        read_only_fields = (
            "telegram_chat_id",
            "telegram_username",
            "telegram_is_connected",
            "last_sent_at",
            "last_status",
            "last_error",
        )

    def validate(self, attrs):
        send_email = attrs.get("send_email", getattr(self.instance, "send_email", False))
        email_to = attrs.get("email_to", getattr(self.instance, "email_to", None))
        send_telegram = attrs.get("send_telegram", getattr(self.instance, "send_telegram", False))
        telegram_chat_id = getattr(self.instance, "telegram_chat_id", None)

        if send_email and not (email_to or "").strip():
            raise serializers.ValidationError({"email_to": ["Укажите email для отправки отчёта."]})

        if send_telegram and not telegram_chat_id:
            raise serializers.ValidationError(
                {"send_telegram": ["Telegram не подключён. Нажмите 'Подключить Telegram'."]}
            )

        enabled = attrs.get("enabled", getattr(self.instance, "enabled", False))
        if enabled and not send_email and not send_telegram:
            raise serializers.ValidationError(
                {"enabled": ["Выберите хотя бы один канал доставки для ежедневного отчёта."]}
            )

        return attrs


class ReportLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportLog
        fields = (
            "id",
            "period_from",
            "period_to",
            "created_at",
            "status",
            "trigger_type",
            "file_path",
            "delivery_channels",
            "error",
        )


class ReportGenerateSerializer(serializers.Serializer):
    period_from = serializers.DateField(required=False)
    period_to = serializers.DateField(required=False)

    def validate(self, attrs):
        period_from = attrs.get("period_from")
        period_to = attrs.get("period_to")
        if period_from and period_to and period_from > period_to:
            raise serializers.ValidationError({"period_from": ["period_from must be <= period_to"]})
        return attrs
