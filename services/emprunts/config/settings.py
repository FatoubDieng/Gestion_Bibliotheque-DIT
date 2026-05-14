"""
DIT Bibliothèque — Service Emprunts
Django Settings
"""
import os
import dj_database_url
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY    = os.environ.get('DJANGO_SECRET_KEY', 'dev-key-emprunts-insecure')
DEBUG         = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'rest_framework',
    'corsheaders',
    'emprunts_app',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'config.urls'

DATABASES = {
    'default': dj_database_url.parse(
        os.environ.get(
            'DATABASE_URL',
            'postgresql://dit_user:dit_secret@localhost:5432/dit_bibliotheque'
        )
    )
}

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

CORS_ALLOW_ALL_ORIGINS = True
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE     = 'Africa/Dakar'
USE_I18N      = True
USE_TZ        = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── URLs des autres services (communication inter-services) ──
SERVICE_LIVRES_URL = os.environ.get('SERVICE_LIVRES_URL', 'http://localhost:8001')
SERVICE_USERS_URL  = os.environ.get('SERVICE_USERS_URL',  'http://localhost:8002')

# ── Durée max d'un emprunt (jours) ──────────────────────────
MAX_BORROW_DAYS = int(os.environ.get('MAX_BORROW_DAYS', 14))

# ── Dossier d'export pour le ML ─────────────────────────────
EXPORT_DIR = os.environ.get('EXPORT_DIR', '/app/exports')