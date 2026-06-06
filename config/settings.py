# config/settings.py
from datetime import timedelta
from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ══════════════════════════════════════════════════════════
# SÉCURITÉ
# ══════════════════════════════════════════════════════════
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-v7357b#^q^udvc+p=d-v4o#!ft5+%mn7m0#r(9xbawkxjs6-c3'
)
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# ── ALLOWED_HOSTS ─────────────────────────────────────────
ALLOWED_HOSTS = [
    # Backend hébergé sur Render
    'campus237-api.onrender.com',
    'gestionetablissementbackend.onrender.com',

    # Développement local (Angular tourne sur localhost)
    'localhost',
    '127.0.0.1',

    # Wildcard Render — couvre tous les futurs déploiements .onrender.com
    '.onrender.com',

    #  Vercel — sera ajouté quand le frontend sera déployé
    # 'mon-app.vercel.app',
    # '.vercel.app',
]

# ══════════════════════════════════════════════════════════
# APPLICATIONS
# ══════════════════════════════════════════════════════════
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Tiers
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'drf_spectacular',
    # Apps locales
    'accounts',
    'establishments',
    'comments',
]

# ══════════════════════════════════════════════════════════
# MIDDLEWARE
# CorsMiddleware DOIT être placé le plus haut possible,
# avant SessionMiddleware et CommonMiddleware
# ══════════════════════════════════════════════════════════
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',          # ← Position critique
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ══════════════════════════════════════════════════════════
# BASE DE DONNÉES
# ══════════════════════════════════════════════════════════
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}

# ══════════════════════════════════════════════════════════
# CORS — Configuration complète
#
# Situation actuelle :
#   - Frontend Angular en LOCAL  (localhost:4200)
#   - Backend sur Render         (campus237-api.onrender.com)
#
# Quand le frontend sera sur Vercel, décommente la section
# "Production Vercel" et ajoute l'URL Vercel dans
# CORS_ALLOWED_ORIGINS + ALLOWED_HOSTS.
# ══════════════════════════════════════════════════════════

# Liste explicite des origines autorisées
# (plus sûr que CORS_ALLOW_ALL_ORIGINS = True)
CORS_ALLOWED_ORIGINS = [
    # ── Développement local Angular ───────────────────────
    "http://localhost:4200",
    "http://127.0.0.1:4200",

    # ── Développement local autre port (Live Server, etc.) ─
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:3000",

    # ── Production Vercel (décommente quand déployé) ───────
    # "https://ton-app.vercel.app",
    # "https://ton-app-git-main-toncompte.vercel.app",

    # ── Render preview (optionnel) ─────────────────────────
    # "https://campus237-frontend.onrender.com",
]

# Patterns regex pour les origines dynamiques
# Utile pour Vercel qui génère des URLs de preview uniques par commit
CORS_ALLOWED_ORIGIN_REGEXES = [
    # Couvre toutes les previews Vercel : https://xxx-toncompte.vercel.app
    # Décommente quand le frontend sera sur Vercel
    # r"^https://.*\.vercel\.app$",
]

# Headers que le frontend Angular envoie
# CRITIQUE : sans "authorization", le JWT Bearer est bloqué
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',        # ← JWT Bearer token
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'access-control-allow-origin',
]

# Méthodes HTTP autorisées
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Expose les headers de réponse au JavaScript du frontend
CORS_EXPOSE_HEADERS = [
    'content-type',
    'authorization',
]

# Autorise l'envoi de cookies et credentials cross-origin
# Nécessaire si tu utilises des sessions ou cookies d'auth
CORS_ALLOW_CREDENTIALS = True

# Durée de cache du preflight OPTIONS (en secondes)
CORS_PREFLIGHT_MAX_AGE = 86400  # 24h

# ══════════════════════════════════════════════════════════
# CSRF — Origines de confiance pour les requêtes POST/PUT
# Angular envoie des requêtes JSON donc CSRF n'est pas
# utilisé directement, mais cette liste est nécessaire
# si tu utilises DRF SessionAuthentication ou l'admin Django
# ══════════════════════════════════════════════════════════
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
    "https://campus237-api.onrender.com",
    "https://gestionetablissementbackend.onrender.com",
    # "https://ton-app.vercel.app",   # ← à ajouter lors du déploiement Vercel
]

# ══════════════════════════════════════════════════════════
# VALIDATION MOTS DE PASSE
# ══════════════════════════════════════════════════════════
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ══════════════════════════════════════════════════════════
# INTERNATIONALISATION
# ══════════════════════════════════════════════════════════
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE     = 'Africa/Douala'
USE_I18N      = True
USE_TZ        = True

# ══════════════════════════════════════════════════════════
# FICHIERS STATIQUES
# ══════════════════════════════════════════════════════════
STATIC_URL    = '/static/'
STATIC_ROOT   = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ══════════════════════════════════════════════════════════
# AUTH MODEL
# ══════════════════════════════════════════════════════════
AUTH_USER_MODEL = 'accounts.User'

# ══════════════════════════════════════════════════════════
# DJANGO REST FRAMEWORK
# ══════════════════════════════════════════════════════════
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# ══════════════════════════════════════════════════════════
# SIMPLE JWT
# ══════════════════════════════════════════════════════════
SIMPLE_JWT = {
    # Durées de vie
    'ACCESS_TOKEN_LIFETIME':    timedelta(hours=2),   # 2h pour le dev local confortable
    'REFRESH_TOKEN_LIFETIME':   timedelta(days=7),
    'ROTATE_REFRESH_TOKENS':    True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN':        True,

    # Algorithme de signature
    'ALGORITHM': 'HS256',

    # Header Authorization attendu : "Bearer <token>"
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME':  'HTTP_AUTHORIZATION',

    # Champs utilisateur dans le token
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    # Claims inclus dans le token (vérifier que ton serializer
    # ajoute bien le champ "role" dans le payload JWT)
    'TOKEN_OBTAIN_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenObtainPairSerializer',
}

# ══════════════════════════════════════════════════════════
# DRF SPECTACULAR — Documentation Swagger
# ══════════════════════════════════════════════════════════
SPECTACULAR_SETTINGS = {
    'TITLE':       'Campus237 API',
    'DESCRIPTION': 'API REST pour la gestion des établissements scolaires au Cameroun.',
    'VERSION':     '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'ENUM_NAME_OVERRIDES': {
        'UserStatusEnum':          'accounts.models.UserStatus',
        'EstablishmentStatusEnum': 'establishments.models.EstablishmentStatus',
        'CommentStatusEnum':       'comments.models.CommentStatus',
    },
    # Schéma de sécurité JWT visible dans la doc Swagger
    'SECURITY': [{'BearerAuth': []}],
    'COMPONENTS': {
        'securitySchemes': {
            'BearerAuth': {
                'type':         'http',
                'scheme':       'bearer',
                'bearerFormat': 'JWT',
            }
        }
    },
}