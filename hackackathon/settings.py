# Copyright (C) 2025-now  p.fernandezf <p@fernandezf.es> & iago.rivas <delthia@delthia.com>

from datetime import datetime
from zoneinfo import ZoneInfo
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


# Configuración de entorno ----------------------------------------------------
# Host de la web general del evento
HOST_LANDING = os.getenv("HOST_LANDING")
# Host de la web del registro (esta)
HOST_REGISTRO = os.getenv("HOST_REGISTRO")
# -----------------------------------------------------------------------------


# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

SECRET_KEY_FALLBACKS = [
    os.getenv("SECRET_KEY_FALLBACK"),
]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [HOST_REGISTRO]

if DEBUG:
    ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = [
    "https://" + HOST_REGISTRO,
]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "gestion",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.auth.middleware.LoginRequiredMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "hackackathon.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "hackackathon.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "es-es"

TIME_ZONE = "Europe/Madrid"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"
STATICFILES_DIRS = [
    BASE_DIR / "staticfiles",
]

# Media files (User uploaded content)
# https://docs.djangoproject.com/en/5.1/topics/files/
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "media/"

# Fixtures (initial data)
# https://docs.djangoproject.com/en/5.1/topics/db/fixtures/
FIXTURE_DIRS = [
    BASE_DIR / "fixtures",
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Login
# https://docs.djangoproject.com/en/5.1/ref/settings/#login-url
LOGIN_URL = "/login"

# Messages
# https://docs.djangoproject.com/en/5.1/ref/contrib/messages/
MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

# Email
# https://docs.djangoproject.com/en/5.1/topics/email/
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Configuración de entorno ----------------------------------------------------
# Inicio del evento
FECHA_INICIO_EVENTO = datetime.fromisoformat(os.getenv("FECHA_INICIO_EVENTO")).replace(
    tzinfo=ZoneInfo(TIME_ZONE)
)
# Fin del evento
FECHA_FIN_EVENTO = datetime.fromisoformat(os.getenv("FECHA_FIN_EVENTO")).replace(
    tzinfo=ZoneInfo(TIME_ZONE)
)
# Fin del plazo de registro
FECHA_FIN_REGISTRO = datetime.fromisoformat(os.getenv("FECHA_FIN_REGISTRO")).replace(
    tzinfo=ZoneInfo(TIME_ZONE)
)

# Nombre y mail del administrador
NOMBRE_ADMIN = os.getenv("NOMBRE_ADMIN")
MAIL_ADMIN = os.getenv("MAIL_ADMIN")

# Asuntos de los correos
EMAIL_VERIFICACION_ASUNTO = "HackUDC 2026 - Confirma tu correo ✉️"
EMAIL_CONFIRMACION_ASUNTO = "HackUDC 2026 - Confirma tu plaza! <emoji>"
# -----------------------------------------------------------------------------

ADMINS = [
    (NOMBRE_ADMIN, MAIL_ADMIN),
]
