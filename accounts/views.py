# accounts/views.py
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .emails import envoyer_email_bannissement, envoyer_email_suspension
from .models import User, UserRole, UserStatus
from .permissions import IsAdmin
from .serializers import (
    AdminUserSerializer,
    LoginSerializer,
    LogoutSerializer,
    RegisterSerializer,
    StatutUpdateSerializer,
    UserSerializer,
)


# ─────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────

class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    @extend_schema(
        summary='Inscrire un utilisateur ou un directeur',
        responses={201: UserSerializer},
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Connecter un compte et retourner les tokens JWT',
        request=LoginSerializer,
        responses={200: OpenApiResponse(description='Tokens JWT, utilisateur et redirection')},
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class MeView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Deconnecter un compte en blacklistant son refresh token',
        request=LogoutSerializer,
        responses={204: None},
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ─────────────────────────────────────────
# ADMIN — Gestion des utilisateurs
# ─────────────────────────────────────────

class AdminUserListView(generics.ListAPIView):
    """
    [ADMIN] Liste tous les comptes (directeurs + utilisateurs).
    Exclut les comptes admin.
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = AdminUserSerializer

    @extend_schema(
        summary='[Admin] Lister tous les comptes utilisateurs',
        responses={200: AdminUserSerializer(many=True)},
    )
    def get_queryset(self):
        qs = User.objects.exclude(role=UserRole.ADMIN)

        # Filtres optionnels via query params
        role   = self.request.query_params.get('role')
        statut = self.request.query_params.get('statut')

        if role:
            qs = qs.filter(role=role)
        if statut:
            qs = qs.filter(statut=statut)

        return qs


class AdminUserDetailView(generics.RetrieveAPIView):
    """[ADMIN] Détail d'un compte utilisateur."""
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = AdminUserSerializer
    queryset = User.objects.exclude(role=UserRole.ADMIN)

    @extend_schema(
        summary='[Admin] Détail d\'un compte utilisateur',
        responses={200: AdminUserSerializer},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class AdminUserStatutView(APIView):
    """
    [ADMIN] Modifier le statut d'un compte : actif / suspendu / banni.
    Envoie automatiquement un email si suspension ou bannissement.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        summary='[Admin] Modifier le statut d\'un utilisateur',
        request=StatutUpdateSerializer,
        responses={
            200: AdminUserSerializer,
            400: OpenApiResponse(description='Données invalides'),
            404: OpenApiResponse(description='Utilisateur introuvable'),
        },
    )
    def patch(self, request, pk):
        try:
            user = User.objects.exclude(role=UserRole.ADMIN).get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Utilisateur introuvable.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = StatutUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        nouveau_statut = serializer.validated_data['statut']
        ancien_statut  = user.statut

        # Aucun changement → on répond quand même 200 proprement
        if nouveau_statut == ancien_statut:
            return Response(AdminUserSerializer(user).data, status=status.HTTP_200_OK)

        # Mise à jour du statut
        user.statut = nouveau_statut

        # Synchronise is_active avec le statut
        user.is_active = (nouveau_statut == UserStatus.ACTIF)
        user.save(update_fields=['statut', 'is_active'])

        # Envoi d'email uniquement si suspension ou bannissement
        try:
            if nouveau_statut == UserStatus.SUSPENDU:
                envoyer_email_suspension(user)
            elif nouveau_statut == UserStatus.BANNI:
                envoyer_email_bannissement(user)
        except Exception:
            # L'email échoue → on ne bloque pas l'action admin
            pass

        return Response(AdminUserSerializer(user).data, status=status.HTTP_200_OK)