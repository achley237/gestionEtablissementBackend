# Campus237 — Backend API

API REST pour la gestion des établissements scolaires, développée avec Django et Django REST Framework.

## Table des matières

- [Aperçu](#aperçu)
- [Stack technique](#stack-technique)
- [Architecture du projet](#architecture-du-projet)
- [Installation locale](#installation-locale)
- [Variables d'environnement](#variables-denvironnement)
- [Endpoints API](#endpoints-api)
- [Authentification](#authentification)
- [Gestion des utilisateurs (Admin)](#gestion-des-utilisateurs-admin)
- [Établissements](#établissements)
- [Commentaires](#commentaires)
- [Déploiement sur Render](#déploiement-sur-render)

---

## Aperçu

Campus237 est une plateforme de gestion des établissements scolaires au Cameroun. Le backend expose une API REST sécurisée par JWT, permettant à trois types d'utilisateurs (Administrateur, Directeur, Utilisateur) de gérer les établissements, les équipements, les commentaires et les comptes utilisateurs.

---

## Stack technique

| Technologie | Rôle |
|---|---|
| Python 3.14 | Langage |
| Django 5.2 | Framework web |
| Django REST Framework | API REST |
| SimpleJWT | Authentification JWT |
| drf-spectacular | Documentation Swagger/OpenAPI |
| PostgreSQL | Base de données (production) |
| SQLite | Base de données (développement) |
| Gunicorn | Serveur WSGI (production) |
| WhiteNoise | Fichiers statiques |
| Render | Hébergement cloud |

---

## Architecture du projet

```
campus237-backend/
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/           # Gestion des utilisateurs et authentification
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── permissions.py
│   ├── emails.py
│   └── urls.py
├── establishments/     # Gestion des établissements
├── comments/           # Gestion des commentaires
├── manage.py
├── requirements.txt
└── .env
```

---

## Installation locale

### Prérequis

- Python 3.10+
- Git

### Étapes

```bash
# 1. Cloner le projet
git clone https://github.com/achley237/gestionEtablissement.git
cd gestionEtablissement

# 2. Créer et activer l'environnement virtuel
python -m venv env
env\Scripts\activate        # Windows
source env/bin/activate     # Linux/Mac

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
copy .env.example .env      # Windows
cp .env.example .env        # Linux/Mac
# Remplir les valeurs dans .env

# 5. Appliquer les migrations
python manage.py migrate

# 6. Créer un superutilisateur admin
python manage.py createsuperuser

# 7. Lancer le serveur
python manage.py runserver
```

L'API sera disponible sur : `http://localhost:8000/api/`
La documentation Swagger : `http://localhost:8000/api/docs/`

---

## Variables d'environnement

Copie `.env.example` en `.env` et remplis les valeurs :

```env
# Sécurité
SECRET_KEY=ta_cle_secrete_django
DEBUG=True

# Base de données (laisser vide en local pour utiliser SQLite)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Email (Gmail)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=ton.email@gmail.com
EMAIL_HOST_PASSWORD=ton_app_password_gmail
DEFAULT_FROM_EMAIL=Campus237 <noreply@campus237.cm>
```

> **Gmail** : Utilise un **App Password** et non ton mot de passe principal. Active d'abord la validation en 2 étapes sur [myaccount.google.com](https://myaccount.google.com).

---

## Endpoints API

Base URL : `https://gestionetablissementbackend.onrender.com/api/`

Documentation interactive : `https://gestionetablissementbackend.onrender.com/api/docs/`

---

## Authentification

| Méthode | Endpoint | Description | Accès |
|---|---|---|---|
| `POST` | `/accounts/register/` | Créer un compte (utilisateur ou directeur) | Public |
| `POST` | `/accounts/login/` | Connexion — retourne les tokens JWT | Public |
| `POST` | `/accounts/logout/` | Déconnexion — blackliste le refresh token | Authentifié |
| `GET` | `/accounts/me/` | Profil de l'utilisateur connecté | Authentifié |

### Exemple de connexion

```json
POST /api/accounts/login/
{
  "email": "utilisateur@example.com",
  "password": "motdepasse123"
}
```

Réponse :
```json
{
  "access": "eyJ...",
  "refresh": "eyJ...",
  "user": {
    "id": 1,
    "nom": "Dupont",
    "prenom": "Jean",
    "email": "utilisateur@example.com",
    "role": "directeur",
    "statut": "actif"
  },
  "redirect_to": "/dashboard/directeur"
}
```

### Utilisation du token

Ajoute le header suivant à chaque requête protégée :
```
Authorization: Bearer <access_token>
```

### Rôles utilisateurs

| Rôle | Valeur | Redirection |
|---|---|---|
| Administrateur | `admin` | `/dashboard/admin` |
| Directeur | `directeur` | `/dashboard/directeur` |
| Utilisateur | `utilisateur` | `/dashboard/utilisateur` |

---

## Gestion des utilisateurs (Admin)

Ces endpoints sont réservés aux utilisateurs avec le rôle `admin`.

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/accounts/admin/users/` | Liste tous les comptes (hors admins) |
| `GET` | `/accounts/admin/users/?role=directeur` | Filtrer par rôle |
| `GET` | `/accounts/admin/users/?statut=suspendu` | Filtrer par statut |
| `GET` | `/accounts/admin/users/{id}/` | Détail d'un compte |
| `PATCH` | `/accounts/admin/users/{id}/statut/` | Modifier le statut d'un compte |

### Statuts disponibles

| Statut | Effet |
|---|---|
| `actif` | Accès normal au système |
| `suspendu` | Accès bloqué + email envoyé automatiquement |
| `banni` | Accès bloqué définitivement + email envoyé automatiquement |

### Exemple — Suspendre un compte

```json
PATCH /api/accounts/admin/users/5/statut/
{
  "statut": "suspendu",
  "raison": "Comportement inapproprié signalé"
}
```

Réponse `200 OK` :
```json
{
  "id": 5,
  "nom": "Kamdem",
  "prenom": "Paul",
  "email": "paul@example.com",
  "role": "utilisateur",
  "statut": "suspendu",
  ...
}
```

Un email de notification est automatiquement envoyé à l'utilisateur concerné.

---

## Établissements

| Méthode | Endpoint | Description | Accès |
|---|---|---|---|
| `GET` | `/establishments/` | Liste des établissements | Authentifié |
| `POST` | `/establishments/` | Créer un établissement | Directeur / Admin |
| `GET` | `/establishments/{id}/` | Détail d'un établissement | Authentifié |
| `PUT/PATCH` | `/establishments/{id}/` | Modifier un établissement | Directeur / Admin |
| `DELETE` | `/establishments/{id}/` | Supprimer un établissement | Admin |

---

## Commentaires

| Méthode | Endpoint | Description | Accès |
|---|---|---|---|
| `GET` | `/comments/` | Liste des commentaires | Authentifié |
| `POST` | `/comments/` | Ajouter un commentaire | Authentifié |
| `GET` | `/comments/{id}/` | Détail d'un commentaire | Authentifié |
| `DELETE` | `/comments/{id}/` | Supprimer un commentaire | Admin |

---

## Déploiement sur Render

### Variables d'environnement à configurer dans Render

| Clé | Valeur |
|---|---|
| `SECRET_KEY` | Clé secrète Django |
| `DEBUG` | `False` |
| `DATABASE_URL` | URL interne PostgreSQL Render |
| `EMAIL_HOST_USER` | Email Gmail |
| `EMAIL_HOST_PASSWORD` | App Password Gmail |
| `DEFAULT_FROM_EMAIL` | `Campus237 <noreply@campus237.cm>` |

### Commandes de build (Render)

```bash
# Build command
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate

# Start command
gunicorn config.wsgi:application
```


## Licence

Projet académique — tous droits réservés © 2026 ISJ FOULEFACK DANIELLE.