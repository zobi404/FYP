from .base import *
import os
import dj_database_url

DEBUG = False
ALLOWED_HOSTS = ["https://fyp-production-dc9d.up.railway.app", "localhost", "https://qa-verse.vercel.app", "https://qa-verse-e52bd37vc-malik-umairs-projects.vercel.app", "*"]

CSRF_TRUSTED_ORIGINS = [
    'https://fyp-production-dc9d.up.railway.app',   
    'https://*.railway.app',
    'https://qa-verse.vercel.app',
    'https://qa-verse-e52bd37vc-malik-umairs-projects.vercel.app',
    '*'
]

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

STATIC_ROOT = BASE_DIR / "staticfiles"
