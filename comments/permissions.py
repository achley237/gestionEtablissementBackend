from rest_framework.permissions import SAFE_METHODS, BasePermission

from accounts.models import UserRole


class CommentPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        if not request.user or not request.user.is_authenticated:
            return False

        if view.action in {'approve', 'reject', 'destroy'}:
            return request.user.role == UserRole.ADMIN

        if view.action == 'create':
            return request.user.role in {
                UserRole.UTILISATEUR,
                UserRole.DIRECTEUR,
                UserRole.ADMIN,
            }

        return True

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        if request.user.role == UserRole.ADMIN:
            return True

        if view.action in {'update', 'partial_update'}:
            return obj.auteur_id == request.user.id

        return False


class AdminCommentPermission(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == UserRole.ADMIN
        )
