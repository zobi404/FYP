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
    'https://fyp-production-dc9d.up.railway.app',
]

CORS_ALLOWED_ORIGINS = [
    "https://qa-verse.vercel.app",
    "https://qa-verse-e52bd37vc-malik-umairs-projects.vercel.app",
    "http://localhost:3000",
]

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

STATIC_ROOT = BASE_DIR / "staticfiles"

# Email Settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
