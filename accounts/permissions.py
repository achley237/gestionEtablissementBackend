# accounts/permissions.py
from rest_framework.permissions import BasePermission
from .models import UserRole


class IsAdmin(BasePermission):
    """Autorise uniquement les utilisateurs avec le rôle ADMIN."""
    message = "Accès réservé aux administrateurs."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == UserRole.ADMIN
        )