from datetime import timedelta
from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================================
# SECURITE
# ==========================================

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = os.environ.get("DEBUG", "False") == "True"

ALLOWED_HOSTS = [
    "gestionetablissementbackend.onrender.com",
    "localhost",
    "127.0.0.1",
]

# ==========================================
# APPLICATIONS
# ==========================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "corsheaders",

    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",

    "accounts",
    "establishments",
    "comments",
]

# ==========================================
# MIDDLEWARE
# ==========================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "corsheaders.middleware.CorsMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

# ==========================================
# TEMPLATES
# ==========================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ==========================================
# DATABASE
# ==========================================

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}

# ==========================================
# PASSWORDS
# ==========================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"
    },
]

# ==========================================
# INTERNATIONALISATION
# ==========================================

LANGUAGE_CODE = "fr-fr"

TIME_ZONE = "Africa/Douala"

USE_I18N = True
USE_TZ = True

# ==========================================
# STATIC FILES
# ==========================================

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)

# ==========================================
# USER MODEL
# ==========================================

AUTH_USER_MODEL = "accounts.User"

# ==========================================
# CORS
# ==========================================

CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",
    "https://gestion-des-etablissements-front-en-fawn.vercel.app",
]

CORS_ALLOW_CREDENTIALS = True

# ==========================================
# CSRF
# ==========================================

CSRF_TRUSTED_ORIGINS = [
    "https://gestion-des-etablissements-front-en-fawn.vercel.app",
]

# ==========================================
# HTTPS
# ==========================================

SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# ==========================================
# DJANGO REST FRAMEWORK
# ==========================================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": (
        "drf_spectacular.openapi.AutoSchema"
    ),
}

# ==========================================
# JWT
# ==========================================

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),

    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,

    "UPDATE_LAST_LOGIN": True,
}

# ==========================================
# SWAGGER
# ==========================================

SPECTACULAR_SETTINGS = {
    "TITLE": "Campus237 API",
    "DESCRIPTION": "API REST pour la gestion des établissements scolaires",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,

    "ENUM_NAME_OVERRIDES": {
        "UserStatusEnum": "accounts.models.UserStatus",
        "EstablishmentStatusEnum": "establishments.models.EstablishmentStatus",
        "CommentStatusEnum": "comments.models.CommentStatus",
    },
}

# ==========================================
# EMAIL
# ==========================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST    = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT    = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'

EMAIL_HOST_USER     = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

DEFAULT_FROM_EMAIL = os.environ.get(
    'DEFAULT_FROM_EMAIL',
    'Campus237 <noreply@campus237.cm>'
)