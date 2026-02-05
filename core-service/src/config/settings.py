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
    "django_celery_beat",
    "apps.oauth",
    "apps.todo",
    "rest_framework",
    "drf_spectacular"
]

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
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

SPECTACULAR_SETTINGS = {
    'TITLE': 'TODO Core Microservice',
    'DESCRIPTION': 'Tasks management service',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

AUTHENTICATION_BACKENDS = [
    "apps.oauth.authentication.DjangoOAuthBackend",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    # "django.contrib.messages.middleware.MessageMiddleware",
]

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://:{}@{}:{}/{}".format(
            os.environ.get("REDIS_PASS", ""),
            os.environ.get("REDIS_HOST", "localhost"),
            os.environ.get("REDIS_PORT", "6379"),
            os.environ.get("REDIS_DB", "0"),
        ),
    }
}

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

USE_TZ = False

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Celery

CELERY_TIMEZONE = "UTC"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BROKER_URL = "redis://:{}@{}:{}/{}".format(
    os.environ.get("REDIS_PASS", ""),
    os.environ.get("REDIS_HOST", "localhost"),
    os.environ.get("REDIS_PORT", "6379"),
    os.environ.get("REDIS_DB", "0"),
)
CELERY_RESULT_BACKEND = "redis://:{}@{}:{}/{}".format(
    os.environ.get("REDIS_PASS", ""),
    os.environ.get("REDIS_HOST", "localhost"),
    os.environ.get("REDIS_PORT", "6379"),
    os.environ.get("REDIS_DB", "0"),
)
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_SES_REGION_NAME = os.environ.get("AWS_SES_REGION_NAME")
AWS_SES_ENDPOINT_URL = os.environ.get("AWS_SES_ENDPOINT_URL")
AWS_SES_SENDER_EMAIL = os.environ.get("AWS_SES_SENDER_EMAIL")
AWS_SES_MAX_RECIPIENTS_PER_MESSAGE = int(
    os.environ.get("AWS_SES_MAX_RECIPIENTS_PER_MESSAGE", 50)
)

# KAFKA_TOPICS=
KAFKA_BOOTSTRAP_SERVERS: list[str] = [
    server.strip()
    for server in str(os.environ.get("KAFKA_BOOTSTRAP_SERVERS")).split(",")
]
KAFKA_MODEL_EVENTS_TOPIC = os.environ.get("KAFKA_MODEL_EVENTS_TOPIC")
