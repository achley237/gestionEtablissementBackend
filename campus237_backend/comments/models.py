from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class CommentStatus(models.TextChoices):
    EN_ATTENTE = 'en_attente', 'En attente'
    APPROUVE = 'approuve', 'Approuve'
    REJETE = 'rejete', 'Rejete'


class Comment(models.Model):
    contenu = models.TextField()
    note = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='commentaires',
    )
    etablissement = models.ForeignKey(
        'establishments.Establishment',
        on_delete=models.CASCADE,
        related_name='commentaires',
    )
    statut = models.CharField(
        max_length=20,
        choices=CommentStatus.choices,
        default=CommentStatus.EN_ATTENTE,
    )
    motif_rejet = models.TextField(blank=True)
    date_publication = models.DateTimeField(default=timezone.now)
    date_mise_a_jour = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_publication']
        constraints = [
            models.UniqueConstraint(
                fields=['auteur', 'etablissement'],
                name='unique_comment_per_user_establishment',
            )
        ]
        indexes = [
            models.Index(fields=['statut']),
            models.Index(fields=['etablissement', 'statut']),
        ]

    def __str__(self):
        return f'{self.auteur.email} - {self.etablissement.nom}'
