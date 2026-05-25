from django.conf import settings
from django.db import models
from django.utils import timezone


class EstablishmentType(models.TextChoices):
    PRIMAIRE = 'primaire', 'Primaire'
    SECONDAIRE = 'secondaire', 'Secondaire'
    LYCEE = 'lycee', 'Lycee'
    UNIVERSITE = 'universite', 'Universite'
    AUTRE = 'autre', 'Autre'


class EstablishmentStatus(models.TextChoices):
    BROUILLON = 'brouillon', 'Brouillon'
    EN_ATTENTE = 'en_attente', 'En attente'
    PUBLIE = 'publie', 'Publie'
    REJETE = 'rejete', 'Rejete'
    ARCHIVE = 'archive', 'Archive'


class Establishment(models.Model):
    nom = models.CharField(max_length=255)
    type = models.CharField(max_length=30, choices=EstablishmentType.choices)
    adresse = models.TextField()
    ville = models.CharField(max_length=100)
    region = models.CharField(max_length=100, blank=True)
    pays = models.CharField(max_length=100, default='Cameroun')
    telephone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    site_web = models.URLField(blank=True)
    niveaux_scolaires = models.JSONField(default=list, blank=True)
    capacite = models.PositiveIntegerField(null=True, blank=True)
    annee_creation = models.PositiveIntegerField(null=True, blank=True)
    statut = models.CharField(
        max_length=30,
        choices=EstablishmentStatus.choices,
        default=EstablishmentStatus.EN_ATTENTE,
    )
    motif_rejet = models.TextField(blank=True)
    directeur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='etablissements',
        null=True,
        blank=True,
    )
    date_creation = models.DateTimeField(default=timezone.now)
    date_mise_a_jour = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nom']
        indexes = [
            models.Index(fields=['statut']),
            models.Index(fields=['ville']),
            models.Index(fields=['type']),
        ]

    def __str__(self):
        return self.nom
