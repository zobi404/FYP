from .base import *
import os
import dj_database_url

DEBUG = True
ALLOWED_HOSTS = ["qaverse-staging.up.railway.app", "localhost"]

CSRF_TRUSTED_ORIGINS = [
    'https://qaverse-staging.up.railway.app',  
    'https://*.railway.app',  
]

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

STATIC_ROOT = BASE_DIR / "staticfiles"
