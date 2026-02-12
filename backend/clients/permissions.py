from clients.models import Client
from rest_framework import permissions
from rest_framework.exceptions import AuthenticationFailed


class HasValidApiKey(permissions.BasePermission):
    header_name = "HTTP_X_API_KEY"

    def has_permission(self, request, view):
        if request.method == "OPTIONS":
            return True
        api_key = request.META.get(self.header_name)
        if not api_key:
            api_key = request.query_params.get("api_key")
        if not api_key and request.method in ("POST", "PUT", "PATCH"):
            api_key = request.data.get("api_key")
        if not api_key:
            raise AuthenticationFailed("Отсутствует API-ключ.")
        try:
            client = Client.objects.get(api_key=api_key, is_active=True)
        except Client.DoesNotExist as exc:
            raise AuthenticationFailed("Недействительный API-ключ или клиент отключен.") from exc
        request.client = client
        return True
