# accounts/emails.py
from django.core.mail import send_mail
from django.conf import settings


SUJET_SUSPENSION = "⚠️ Votre compte a été suspendu"
SUJET_BANNISSEMENT = "🚫 Votre compte a été banni"

CORPS_SUSPENSION = """
Bonjour {prenom} {nom},

Nous vous informons que votre compte sur la plateforme Campus237 a été
temporairement suspendu par un administrateur.

Vous ne pouvez plus vous connecter tant que votre compte reste suspendu.

Si vous pensez qu'il s'agit d'une erreur, veuillez contacter le support.

Cordialement,
L'équipe Campus237
"""

CORPS_BANNISSEMENT = """
Bonjour {prenom} {nom},

Nous vous informons que votre compte sur la plateforme Campus237 a été
définitivement banni par un administrateur.

Vous n'avez plus accès à la plateforme.

Si vous pensez qu'il s'agit d'une erreur, veuillez contacter le support.

Cordialement,
L'équipe Campus237
"""


def envoyer_email_suspension(user):
    """Envoie un email à l'utilisateur lorsque son compte est suspendu."""
    send_mail(
        subject=SUJET_SUSPENSION,
        message=CORPS_SUSPENSION.format(prenom=user.prenom, nom=user.nom),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def envoyer_email_bannissement(user):
    """Envoie un email à l'utilisateur lorsque son compte est banni."""
    send_mail(
        subject=SUJET_BANNISSEMENT,
        message=CORPS_BANNISSEMENT.format(prenom=user.prenom, nom=user.nom),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )