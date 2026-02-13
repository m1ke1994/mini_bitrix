import logging

from django.contrib.auth import authenticate
from rest_framework import permissions, status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.serializers import RegisterResponseSerializer, RegisterSerializer

logger = logging.getLogger(__name__)


def _format_errors(errors):
    return {"errors": errors}


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [JSONRenderer]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning("Register validation failed: %s", serializer.errors)
            return Response(_format_errors(serializer.errors), status=status.HTTP_400_BAD_REQUEST)

        user, client, _client_user = serializer.save()
        response_serializer = RegisterResponseSerializer(
            {
                "user_id": user.id,
                "email": user.email,
                "client_id": client.id,
                "company_name": client.name,
                "api_key": client.api_key,
            }
        )
        tokens = RefreshToken.for_user(user)
        return Response(
            {
                "user": response_serializer.data,
                "tokens": {
                    "access": str(tokens.access_token),
                    "refresh": str(tokens),
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [JSONRenderer]

    def post(self, request, *args, **kwargs):
        email = (request.data.get("email") or "").strip().lower()
        password = request.data.get("password") or ""

        validation_errors = {}
        if not email:
            validation_errors["email"] = ["Укажите email."]
        if not password:
            validation_errors["password"] = ["Укажите пароль."]
        if validation_errors:
            logger.warning("Login validation failed: %s", validation_errors)
            return Response(_format_errors(validation_errors), status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request=request, email=email, password=password)
        if user is None:
            logger.warning("Login failed: invalid credentials for email=%s", email)
            return Response(
                _format_errors({"non_field_errors": ["Неверный email или пароль."]}),
                status=status.HTTP_401_UNAUTHORIZED,
            )

        client_user = getattr(user, "client_user", None)
        if client_user is None or not client_user.is_active:
            logger.warning("Login failed: inactive client user for email=%s", email)
            return Response(
                _format_errors({"non_field_errors": ["Доступ в кабинет клиента отключен."]}),
                status=status.HTTP_401_UNAUTHORIZED,
            )

        tokens = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(tokens.access_token),
                "refresh": str(tokens),
                "email": user.email,
                "client_id": client_user.client_id,
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [JSONRenderer]

    def post(self, request, *args, **kwargs):
        return Response({"detail": "Вы вышли из системы."}, status=status.HTTP_200_OK)
