import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

JWT_PUBLIC_KEY = os.environ.get("JWT_PUBLIC_KEY")

DEBUG = bool(os.environ.get("DEBUG", default=0))

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1").split(",")

# Application definition
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.oauth",
    "apps.todo",
    "rest_framework",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.oauth.authentication.OAuth2Authentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "apps.oauth.permissions.IsVerifiedAndAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}

AUTHENTICATION_BACKENDS = [
    "apps.oauth.authentication.DjangoOAuthBackend",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    # "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "config.urls"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.{}".format(
            os.environ.get("DATABASE_ENGINE", "postgresql")
        ),
        "NAME": os.environ.get("DATABASE_NAME", "todo-core"),
        "USER": os.environ.get("DATABASE_USERNAME", "myprojectuser"),
        "PASSWORD": os.environ.get("DATABASE_PASSWORD", "password"),
        "HOST": os.environ.get("DATABASE_HOST", "127.0.0.1"),
        "PORT": os.environ.get("DATABASE_PORT", 5432),
        "OPTIONS": {"options": "-c search_path=core"},
    }
}

AUTH_USER_MODEL = "oauth.Users"

# Internationalization
LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
