from rest_framework import permissions


class IsClientUser(permissions.BasePermission):
    message = "Client dashboard access is available only for active client users."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        client_user = getattr(user, "client_user", None)
        if client_user is None:
            return False
        if not client_user.is_active:
            return False
        request.client = client_user.client
        return True
