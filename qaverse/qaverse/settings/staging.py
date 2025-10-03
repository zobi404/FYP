from .base import *

DEBUG = False
ALLOWED_HOSTS = ["qaverse-staging.up.railway.app", "localhost"]

CSRF_TRUSTED_ORIGINS = [
    'https://qaverse-staging.up.railway.app',  
    'https://*.railway.app',  
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

STATIC_ROOT = BASE_DIR / "staticfiles"
