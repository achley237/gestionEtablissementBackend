from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from establishments.models import Establishment
from .models import Comment, CommentStatus
from .permissions import AdminCommentPermission, CommentPermission
from .serializers import (
    AdminCommentSerializer,
    CommentModerationSerializer,
    CommentSerializer,
    EstablishmentRatingSerializer,
)


@extend_schema_view(
    list=extend_schema(summary='Lister les commentaires approuves d’un etablissement'),
    create=extend_schema(summary='Laisser un commentaire sur un etablissement'),
)
class EstablishmentCommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [CommentPermission]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_establishment(self):
        return get_object_or_404(Establishment, pk=self.kwargs['establishment_pk'])

    def get_queryset(self):
        queryset = Comment.objects.select_related('auteur', 'etablissement').filter(
            etablissement_id=self.kwargs['establishment_pk']
        )
        user = self.request.user

        if user.is_authenticated and getattr(user, 'role', None) == 'admin':
            return queryset
        if user.is_authenticated:
            return queryset.filter(
                models_q_approved_or_mine(user.id)
            )
        return queryset.filter(statut=CommentStatus.APPROUVE)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['etablissement'] = self.get_establishment()
        return context

    def perform_update(self, serializer):
        serializer.save(statut=CommentStatus.EN_ATTENTE, motif_rejet='')

    @extend_schema(
        summary='Obtenir la note moyenne d’un etablissement',
        responses=EstablishmentRatingSerializer,
    )
    @action(detail=False, methods=['get'])
    def rating(self, request, establishment_pk=None):
        establishment = self.get_establishment()
        data = Comment.objects.filter(
            etablissement=establishment,
            statut=CommentStatus.APPROUVE,
        ).aggregate(
            note_moyenne=Avg('note'),
            total_commentaires=Count('id'),
        )
        return Response({
            'etablissement': establishment.id,
            'note_moyenne': round(data['note_moyenne'], 2) if data['note_moyenne'] else 0,
            'total_commentaires': data['total_commentaires'],
        })


@extend_schema_view(
    list=extend_schema(
        summary='Lister tous les commentaires pour moderation, admin seulement',
        parameters=[
            OpenApiParameter('statut', str, description='Filtrer par statut'),
            OpenApiParameter('etablissement', int, description='Filtrer par etablissement'),
        ],
    ),
    retrieve=extend_schema(summary='Consulter un commentaire, admin seulement'),
    destroy=extend_schema(summary='Supprimer un commentaire, admin seulement'),
)
class AdminCommentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = AdminCommentSerializer
    permission_classes = [AdminCommentPermission]
    queryset = Comment.objects.select_related('auteur', 'etablissement')
    http_method_names = ['get', 'delete', 'post', 'head', 'options']

    def get_queryset(self):
        queryset = super().get_queryset()
        statut = self.request.query_params.get('statut')
        etablissement = self.request.query_params.get('etablissement')

        if statut:
            queryset = queryset.filter(statut=statut)
        if etablissement:
            queryset = queryset.filter(etablissement_id=etablissement)
        return queryset

    @extend_schema(summary='Approuver un commentaire', request=None)
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        comment = self.get_object()
        comment.statut = CommentStatus.APPROUVE
        comment.motif_rejet = ''
        comment.save(update_fields=['statut', 'motif_rejet', 'date_mise_a_jour'])
        return Response(self.get_serializer(comment).data)

    @extend_schema(
        summary='Rejeter un commentaire',
        request=CommentModerationSerializer,
    )
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        comment = self.get_object()
        serializer = CommentModerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment.statut = CommentStatus.REJETE
        comment.motif_rejet = serializer.validated_data.get('motif_rejet', '')
        comment.save(update_fields=['statut', 'motif_rejet', 'date_mise_a_jour'])
        return Response(self.get_serializer(comment).data)


def models_q_approved_or_mine(user_id):
    from django.db.models import Q

    return Q(statut=CommentStatus.APPROUVE) | Q(auteur_id=user_id)
