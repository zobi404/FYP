from .base import *

DEBUG = False
ALLOWED_HOSTS = ["https://qaverse-staging.up.railway.app/", "localhost"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

STATIC_ROOT = BASE_DIR / "staticfiles"
