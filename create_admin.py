import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User, UserRole, UserStatus

email = os.environ.get('ADMIN_EMAIL', 'admin@campus237.com')
password = os.environ.get('ADMIN_PASSWORD', 'AdminPass123!')
nom = os.environ.get('ADMIN_NOM', 'Admin')
prenom = os.environ.get('ADMIN_PRENOM', 'Super')

if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(
        email=email,
        password=password,
        nom=nom,
        prenom=prenom,
    )
    print(f"Superuser {email} créé avec succès.")
else:
    print(f"Superuser {email} existe déjà.")