from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone


class UserRole(models.TextChoices):
    UTILISATEUR = 'utilisateur', 'Utilisateur'
    DIRECTEUR = 'directeur', 'Directeur'
    ADMIN = 'admin', 'Administrateur'


class UserStatus(models.TextChoices):
    ACTIF = 'actif', 'Actif'
    SUSPENDU = 'suspendu', 'Suspendu'
    BANNI = 'banni', 'Banni'


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse email est obligatoire.")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', UserRole.ADMIN)
        extra_fields.setdefault('statut', UserStatus.ACTIF)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Un superutilisateur doit avoir is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Un superutilisateur doit avoir is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.UTILISATEUR,
    )
    statut = models.CharField(
        max_length=20,
        choices=UserStatus.choices,
        default=UserStatus.ACTIF,
    )
    fonction = models.CharField(max_length=150, blank=True)
    niveau_acces = models.PositiveSmallIntegerField(default=1)
    date_inscription = models.DateTimeField(default=timezone.now)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom', 'prenom']

    class Meta:
        ordering = ['-date_inscription']

    def __str__(self):
        return f'{self.prenom} {self.nom} <{self.email}>'

    @property
    def redirect_to(self):
        return {
            UserRole.UTILISATEUR: '/dashboard/utilisateur',
            UserRole.DIRECTEUR: '/dashboard/directeur',
            UserRole.ADMIN: '/dashboard/admin',
        }[self.role]
