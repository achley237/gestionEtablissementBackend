from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.models import UserRole
from .models import Establishment, EstablishmentStatus
from .permissions import EstablishmentPermission
from .serializers import (
    EstablishmentModerationSerializer,
    EstablishmentSearchResponseSerializer,
    EstablishmentSerializer,
)

SEARCH_PARAMETERS = [
    OpenApiParameter('q', str, description='Recherche globale dans nom, ville, region, type et niveaux'),
    OpenApiParameter('nom', str, description='Filtrer par nom'),
    OpenApiParameter('ville', str, description='Filtrer par ville'),
    OpenApiParameter('region', str, description='Filtrer par region'),
    OpenApiParameter('pays', str, description='Filtrer par pays'),
    OpenApiParameter('type', str, description='Filtrer par type'),
    OpenApiParameter('niveau', str, description='Filtrer par niveau scolaire'),
    OpenApiParameter('capacite_min', int, description='Capacite minimale'),
    OpenApiParameter('capacite_max', int, description='Capacite maximale'),
    OpenApiParameter('annee_creation_min', int, description='Annee de creation minimale'),
    OpenApiParameter('annee_creation_max', int, description='Annee de creation maximale'),
    OpenApiParameter('ordering', str, description='Tri: nom, ville, type, capacite, annee_creation, date_creation. Prefixer par - pour descendant.'),
]


@extend_schema_view(
    list=extend_schema(
        summary='Lister ou rechercher les etablissements',
        parameters=[
            OpenApiParameter('q', str, description='Recherche globale dans nom, ville, region, type et niveaux'),
            OpenApiParameter('nom', str, description='Filtrer par nom'),
            OpenApiParameter('ville', str, description='Filtrer par ville'),
            OpenApiParameter('region', str, description='Filtrer par region'),
            OpenApiParameter('pays', str, description='Filtrer par pays'),
            OpenApiParameter('type', str, description='Filtrer par type'),
            OpenApiParameter('niveau', str, description='Filtrer par niveau scolaire'),
            OpenApiParameter('statut', str, description='Filtrer par statut, admin seulement'),
            OpenApiParameter('capacite_min', int, description='Capacite minimale'),
            OpenApiParameter('capacite_max', int, description='Capacite maximale'),
            OpenApiParameter('annee_creation_min', int, description='Annee de creation minimale'),
            OpenApiParameter('annee_creation_max', int, description='Annee de creation maximale'),
            OpenApiParameter('ordering', str, description='Tri: nom, ville, type, capacite, annee_creation, date_creation. Prefixer par - pour descendant.'),
        ],
    ),
    create=extend_schema(summary='Ajouter un etablissement'),
    retrieve=extend_schema(summary='Consulter la fiche d’un etablissement'),
    update=extend_schema(summary='Modifier un etablissement'),
    partial_update=extend_schema(summary='Modifier partiellement un etablissement'),
    destroy=extend_schema(summary='Supprimer un etablissement, admin seulement'),
)
class EstablishmentViewSet(viewsets.ModelViewSet):
    serializer_class = EstablishmentSerializer
    permission_classes = [EstablishmentPermission]

    def get_queryset(self):
        user = self.request.user
        queryset = Establishment.objects.select_related('directeur')

        if not user.is_authenticated:
            queryset = queryset.filter(statut=EstablishmentStatus.PUBLIE)
        elif user.role == UserRole.ADMIN:
            pass
        elif user.role == UserRole.DIRECTEUR:
            queryset = queryset.filter(
                Q(statut=EstablishmentStatus.PUBLIE) | Q(directeur_id=user.id)
            )
        else:
            queryset = queryset.filter(statut=EstablishmentStatus.PUBLIE)

        queryset = apply_search_filters(queryset, self.request.query_params)

        statut_etablissement = self.request.query_params.get('statut')
        if statut_etablissement and user.is_authenticated and user.role == UserRole.ADMIN:
            queryset = queryset.filter(statut=statut_etablissement)

        return apply_ordering(queryset, self.request.query_params.get('ordering'))

    @extend_schema(
        summary='Rechercher dans le catalogue public des etablissements publies',
        parameters=SEARCH_PARAMETERS,
        responses=EstablishmentSearchResponseSerializer,
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        queryset = Establishment.objects.select_related('directeur').filter(
            statut=EstablishmentStatus.PUBLIE
        )
        queryset = apply_search_filters(queryset, request.query_params)
        queryset = apply_ordering(queryset, request.query_params.get('ordering'))
        serializer = self.get_serializer(queryset, many=True)
        criteres = {
            key: value
            for key, value in request.query_params.items()
            if key in SEARCH_QUERY_KEYS and value
        }
        return Response({
            'criteres': criteres,
            'count': queryset.count(),
            'results': serializer.data,
        })

    @extend_schema(
        summary='Lister les etablissements du directeur connecte',
        responses=EstablishmentSerializer(many=True),
    )
    @action(detail=False, methods=['get'])
    def mine(self, request):
        queryset = Establishment.objects.select_related('directeur')
        if request.user.role == UserRole.DIRECTEUR:
            queryset = queryset.filter(directeur=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary='Soumettre ou resoumettre un etablissement a validation',
        request=None,
    )
    @action(detail=True, methods=['post'], url_path='submit-for-validation')
    def submit_for_validation(self, request, pk=None):
        establishment = self.get_object()
        establishment.statut = EstablishmentStatus.EN_ATTENTE
        establishment.motif_rejet = ''
        establishment.save(update_fields=['statut', 'motif_rejet', 'date_mise_a_jour'])
        return Response(self.get_serializer(establishment).data)

    @extend_schema(
        summary='Approuver un etablissement, admin seulement',
        request=None,
    )
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        establishment = self.get_object()
        establishment.statut = EstablishmentStatus.PUBLIE
        establishment.motif_rejet = ''
        establishment.save(update_fields=['statut', 'motif_rejet', 'date_mise_a_jour'])
        return Response(self.get_serializer(establishment).data)

    @extend_schema(
        summary='Rejeter un etablissement, admin seulement',
        request=EstablishmentModerationSerializer,
    )
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        establishment = self.get_object()
        serializer = EstablishmentModerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        establishment.statut = EstablishmentStatus.REJETE
        establishment.motif_rejet = serializer.validated_data.get('motif_rejet', '')
        establishment.save(update_fields=['statut', 'motif_rejet', 'date_mise_a_jour'])
        return Response(self.get_serializer(establishment).data)

    @extend_schema(summary='Archiver un etablissement', request=None)
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        establishment = self.get_object()
        establishment.statut = EstablishmentStatus.ARCHIVE
        establishment.save(update_fields=['statut', 'date_mise_a_jour'])
        return Response(self.get_serializer(establishment).data)


SEARCH_QUERY_KEYS = {
    'q',
    'nom',
    'ville',
    'region',
    'pays',
    'type',
    'niveau',
    'capacite_min',
    'capacite_max',
    'annee_creation_min',
    'annee_creation_max',
    'ordering',
}

ORDERING_FIELDS = {
    'nom',
    'ville',
    'type',
    'capacite',
    'annee_creation',
    'date_creation',
}


def apply_search_filters(queryset, params):
    q = params.get('q')
    nom = params.get('nom')
    ville = params.get('ville')
    region = params.get('region')
    pays = params.get('pays')
    type_etablissement = params.get('type')
    niveau = params.get('niveau')

    if q:
        queryset = queryset.filter(
            Q(nom__icontains=q)
            | Q(ville__icontains=q)
            | Q(region__icontains=q)
            | Q(pays__icontains=q)
            | Q(type__icontains=q)
            | Q(niveaux_scolaires__icontains=q)
        )
    if nom:
        queryset = queryset.filter(nom__icontains=nom)
    if ville:
        queryset = queryset.filter(ville__icontains=ville)
    if region:
        queryset = queryset.filter(region__icontains=region)
    if pays:
        queryset = queryset.filter(pays__icontains=pays)
    if type_etablissement:
        queryset = queryset.filter(type=type_etablissement)
    if niveau:
        queryset = queryset.filter(niveaux_scolaires__icontains=niveau)

    queryset = apply_integer_range_filter(queryset, params, 'capacite')
    queryset = apply_integer_range_filter(queryset, params, 'annee_creation')
    return queryset


def apply_integer_range_filter(queryset, params, field_name):
    min_value = parse_positive_int(params.get(f'{field_name}_min'))
    max_value = parse_positive_int(params.get(f'{field_name}_max'))

    if min_value is not None:
        queryset = queryset.filter(**{f'{field_name}__gte': min_value})
    if max_value is not None:
        queryset = queryset.filter(**{f'{field_name}__lte': max_value})
    return queryset


def parse_positive_int(value):
    if value in (None, ''):
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed >= 0 else None


def apply_ordering(queryset, ordering):
    if not ordering:
        return queryset

    direction = '-' if ordering.startswith('-') else ''
    field = ordering[1:] if direction else ordering
    if field not in ORDERING_FIELDS:
        return queryset
    return queryset.order_by(f'{direction}{field}')
