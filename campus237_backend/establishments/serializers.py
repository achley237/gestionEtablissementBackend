from rest_framework import serializers

from accounts.models import UserRole
from .models import Establishment, EstablishmentStatus


class EstablishmentSerializer(serializers.ModelSerializer):
    directeur_email = serializers.EmailField(source='directeur.email', read_only=True)
    directeur_nom = serializers.SerializerMethodField()

    class Meta:
        model = Establishment
        fields = (
            'id',
            'nom',
            'type',
            'adresse',
            'ville',
            'region',
            'pays',
            'telephone',
            'email',
            'site_web',
            'niveaux_scolaires',
            'capacite',
            'annee_creation',
            'statut',
            'motif_rejet',
            'directeur',
            'directeur_email',
            'directeur_nom',
            'date_creation',
            'date_mise_a_jour',
        )
        read_only_fields = (
            'id',
            'statut',
            'motif_rejet',
            'directeur',
            'directeur_email',
            'directeur_nom',
            'date_creation',
            'date_mise_a_jour',
        )

    def get_directeur_nom(self, obj) -> str | None:
        if obj.directeur is None:
            return None
        return f'{obj.directeur.prenom} {obj.directeur.nom}'.strip()

    def validate_niveaux_scolaires(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError('Les niveaux scolaires doivent etre une liste.')
        if any(not isinstance(item, str) for item in value):
            raise serializers.ValidationError('Chaque niveau scolaire doit etre une chaine.')
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['directeur'] = user if user.role == UserRole.DIRECTEUR else None
        validated_data['statut'] = (
            EstablishmentStatus.PUBLIE
            if user.role == UserRole.ADMIN
            else EstablishmentStatus.EN_ATTENTE
        )
        return super().create(validated_data)


class EstablishmentModerationSerializer(serializers.Serializer):
    motif_rejet = serializers.CharField(required=False, allow_blank=True)


class EstablishmentSearchResponseSerializer(serializers.Serializer):
    criteres = serializers.DictField(child=serializers.CharField(), read_only=True)
    count = serializers.IntegerField(read_only=True)
    results = EstablishmentSerializer(many=True, read_only=True)
