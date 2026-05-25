from django.db import IntegrityError
from rest_framework import serializers

from establishments.models import Establishment, EstablishmentStatus
from .models import Comment, CommentStatus


class CommentSerializer(serializers.ModelSerializer):
    auteur_email = serializers.EmailField(source='auteur.email', read_only=True)
    auteur_nom = serializers.SerializerMethodField()
    etablissement_nom = serializers.CharField(source='etablissement.nom', read_only=True)

    class Meta:
        model = Comment
        fields = (
            'id',
            'contenu',
            'note',
            'auteur',
            'auteur_email',
            'auteur_nom',
            'etablissement',
            'etablissement_nom',
            'statut',
            'motif_rejet',
            'date_publication',
            'date_mise_a_jour',
        )
        read_only_fields = (
            'id',
            'auteur',
            'auteur_email',
            'auteur_nom',
            'etablissement',
            'etablissement_nom',
            'statut',
            'motif_rejet',
            'date_publication',
            'date_mise_a_jour',
        )

    def get_auteur_nom(self, obj) -> str:
        return f'{obj.auteur.prenom} {obj.auteur.nom}'.strip()

    def validate(self, attrs):
        request = self.context['request']
        etablissement = self.context['etablissement']

        if etablissement.statut != EstablishmentStatus.PUBLIE:
            raise serializers.ValidationError(
                'Il est possible de commenter uniquement un etablissement publie.'
            )

        if request.method == 'POST' and Comment.objects.filter(
            auteur=request.user,
            etablissement=etablissement,
        ).exists():
            raise serializers.ValidationError(
                'Vous avez deja laisse un commentaire pour cet etablissement.'
            )

        return attrs

    def create(self, validated_data):
        request = self.context['request']
        etablissement = self.context['etablissement']
        try:
            return Comment.objects.create(
                auteur=request.user,
                etablissement=etablissement,
                statut=CommentStatus.EN_ATTENTE,
                **validated_data,
            )
        except IntegrityError as exc:
            raise serializers.ValidationError(
                'Vous avez deja laisse un commentaire pour cet etablissement.'
            ) from exc


class CommentModerationSerializer(serializers.Serializer):
    motif_rejet = serializers.CharField(required=False, allow_blank=True)


class EstablishmentRatingSerializer(serializers.Serializer):
    etablissement = serializers.IntegerField(read_only=True)
    note_moyenne = serializers.FloatField(read_only=True)
    total_commentaires = serializers.IntegerField(read_only=True)


class AdminCommentSerializer(CommentSerializer):
    class Meta(CommentSerializer.Meta):
        read_only_fields = CommentSerializer.Meta.read_only_fields
