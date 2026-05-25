from rest_framework.permissions import SAFE_METHODS, BasePermission

from accounts.models import UserRole


class EstablishmentPermission(BasePermission):
    """
    Lecture publique limitee aux fiches publiees dans la vue.
    Ecriture reservee au directeur proprietaire ou a l'administrateur.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        if not request.user or not request.user.is_authenticated:
            return False

        if view.action == 'create':
            return request.user.role in {UserRole.DIRECTEUR, UserRole.ADMIN}

        if view.action in {'approve', 'reject', 'destroy'}:
            return request.user.role == UserRole.ADMIN

        if view.action in {'mine', 'submit_for_validation', 'archive'}:
            return request.user.role in {UserRole.DIRECTEUR, UserRole.ADMIN}

        return request.user.role in {UserRole.DIRECTEUR, UserRole.ADMIN}

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            if request.user and request.user.is_authenticated:
                if request.user.role == UserRole.ADMIN:
                    return True
                if request.user.role == UserRole.DIRECTEUR and obj.directeur_id == request.user.id:
                    return True
            return obj.statut == 'publie'

        if request.user.role == UserRole.ADMIN:
            return True

        if view.action in {'update', 'partial_update', 'submit_for_validation', 'archive'}:
            return request.user.role == UserRole.DIRECTEUR and obj.directeur_id == request.user.id

        return False
