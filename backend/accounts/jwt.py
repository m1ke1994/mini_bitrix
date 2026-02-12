from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = (attrs.pop("email", "") or "").strip().lower()
        password = attrs.get("password")
        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist as exc:
            raise serializers.ValidationError("User not found.") from exc

        client_user = getattr(user, "client_user", None)
        if client_user is None or not client_user.is_active:
            raise serializers.ValidationError("Client dashboard access is disabled for this account.")

        attrs["username"] = user.get_username()
        data = super().validate(attrs)
        data["email"] = user.email
        data["client_id"] = client_user.client_id
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        client_user = getattr(user, "client_user", None)
        if client_user is not None:
            token["client_id"] = client_user.client_id
        return token
