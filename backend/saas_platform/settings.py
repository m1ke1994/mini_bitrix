import os
from datetime import timedelta
from pathlib import Path

from celery.schedules import crontab
from corsheaders.defaults import default_headers
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR.parent / ".env")

# ================= BASIC =================

_django_secret_key = (os.getenv("DJANGO_SECRET_KEY") or os.getenv("SECRET_KEY") or "").strip()
if not _django_secret_key:
    raise ImproperlyConfigured("DJANGO_SECRET_KEY is required.")

SECRET_KEY = _django_secret_key
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = [
    h.strip()
    for h in os.getenv("ALLOWED_HOSTS", "*").split(",")
    if h.strip()
]


CSRF_TRUSTED_ORIGINS = [
    "https://tracknode.ru",
    "https://www.tracknode.ru",
]

# если используешь nginx + https
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# ================= APPS =================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "django_filters",
    "channels",
    "core",
    "accounts",
    "clients",
    "leads",
    "analytics_app",
    "seo_audit",
    "tracker",
    "telegram_logs",
    "reports",
    "subscriptions",
]

# ================= MIDDLEWARE =================

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "saas_platform.middleware.TrackerCorsMiddleware",
    "django.middleware.security.SecurityMiddleware",

    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "saas_platform.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "saas_platform.wsgi.application"
ASGI_APPLICATION = "saas_platform.asgi.application"

# ================= DATABASE =================

if os.getenv("DJANGO_DB_ENGINE", "postgresql").lower() == "sqlite":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", "mini_saas"),
            "USER": os.getenv("POSTGRES_USER", "mini_saas"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", "mini_saas"),
            "HOST": os.getenv("POSTGRES_HOST", "db"),
            "PORT": int(os.getenv("POSTGRES_PORT", "5432")),
        }
    }

# ================= REDIS =================

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://redis:6379/1"),
    }
}

# ================= LANGUAGE =================

LANGUAGE_CODE = "ru"
LANGUAGES = [("ru", _("Русский"))]
TIME_ZONE = os.getenv("TIME_ZONE", "Europe/Moscow")

USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = [BASE_DIR / "locale"]
DATETIME_FORMAT = "d.m.Y H:i"

# ================= STATIC =================

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DEFAULT_CHARSET = "utf-8"

# ================= CORS =================

CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = list(default_headers) + [
    "authorization",
    "content-type",
]
CORS_ALLOW_METHODS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
]

# ================= DRF =================

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": int(os.getenv("PAGE_SIZE", "20")),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.ScopedRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "public_lead": os.getenv("RATE_LIMIT_PUBLIC_LEAD", "30/minute"),
        "public_event": os.getenv("RATE_LIMIT_PUBLIC_EVENT", "120/minute"),
        "public_analytics_event": os.getenv("RATE_LIMIT_PUBLIC_ANALYTICS_EVENT", "300/minute"),
        "public_telegram_webhook": os.getenv("RATE_LIMIT_PUBLIC_TELEGRAM_WEBHOOK", "120/minute"),
        "public_widget_variant": os.getenv("RATE_LIMIT_PUBLIC_WIDGET_VARIANT", "180/minute"),
    },
}

# ================= JWT =================

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("JWT_ACCESS_MINUTES", "10080"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.getenv("JWT_REFRESH_DAYS", "60"))),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ================= TELEGRAM =================

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME", "").lstrip("@")
TELEGRAM_WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
TELEGRAM_USE_WEBHOOK = os.getenv("TELEGRAM_USE_WEBHOOK", "false").lower() == "true"
TELEGRAM_POLLING_TIMEOUT = int(os.getenv("TELEGRAM_POLLING_TIMEOUT", "30"))
TELEGRAM_POLLING_RETRY_DELAY = float(os.getenv("TELEGRAM_POLLING_RETRY_DELAY", "2"))
TELEGRAM_POLLING_DELETE_WEBHOOK = os.getenv("TELEGRAM_POLLING_DELETE_WEBHOOK", "true").lower() == "true"
TELEGRAM_POLLING_LOCK_FILE = os.getenv("TELEGRAM_POLLING_LOCK_FILE", "/tmp/tracknode_telegram_polling.lock")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")
FRONTEND_URL = os.getenv("FRONTEND_URL", "").rstrip("/")

# ================= PAYMENTS =================

YOOKASSA_SHOP_ID = os.getenv("YOOKASSA_SHOP_ID", "")
YOOKASSA_SECRET_KEY = os.getenv("YOOKASSA_SECRET_KEY", "")
YOOKASSA_RETURN_URL = "https://tracknode.ru/dashboard"
PAYMENT_RETURN_URL = YOOKASSA_RETURN_URL
PAYMENT_CHECKOUT_URL = os.getenv("PAYMENT_CHECKOUT_URL", "")

if YOOKASSA_SECRET_KEY.startswith("live_"):
    if DEBUG:
        raise ImproperlyConfigured("DEBUG must be False when live YooKassa keys are used.")
    if len(SECRET_KEY) < 32:
        raise ImproperlyConfigured("SECRET_KEY must be at least 32 characters in production.")
    if "localhost" in PAYMENT_RETURN_URL or ":9000" in PAYMENT_RETURN_URL:
        raise ImproperlyConfigured("PAYMENT_RETURN_URL cannot contain localhost or :9000 in production.")

# ================= CELERY =================

CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://redis:6379/1")
CELERY_RESULT_BACKEND = os.getenv("REDIS_URL", "redis://redis:6379/1")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Europe/Moscow"
CELERY_BEAT_SCHEDULE = {
    "send_daily_pdf_at_20_msk": {
        "task": "reports.tasks.send_daily_pdf.send_daily_pdf_task",
        "schedule": crontab(hour=20, minute=0),
    },
    "notify_auto_renew_subscriptions_daily": {
        "task": "subscriptions.tasks.notify_auto_renew_subscriptions_task",
        "schedule": crontab(hour=12, minute=0),
    },
    "check_stale_leads_every_30_minutes": {
        "task": "leads.tasks.check_stale_leads",
        "schedule": crontab(minute="*/30"),
    },
}

CHANNELS_USE_INMEMORY = os.getenv("CHANNELS_USE_INMEMORY", "false").lower() == "true"
if CHANNELS_USE_INMEMORY:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        }
    }
else:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {"hosts": [os.getenv("REDIS_URL", "redis://redis:6379/1")]},
        }
    }

# ================= HEALTH =================

HEALTHCHECK_CELERY_PING_ENABLED = os.getenv("HEALTHCHECK_CELERY_PING_ENABLED", "true").lower() == "true"
HEALTHCHECK_REQUIRE_CELERY = os.getenv("HEALTHCHECK_REQUIRE_CELERY", "false").lower() == "true"
HEALTHCHECK_CELERY_PING_TIMEOUT_SECONDS = float(os.getenv("HEALTHCHECK_CELERY_PING_TIMEOUT_SECONDS", "1.5"))

# ================= BACKUPS =================

BACKUP_ENABLED = os.getenv("BACKUP_ENABLED", "false").lower() == "true"
BACKUP_STORAGE_DIR = Path(os.getenv("BACKUP_STORAGE_DIR", str(BASE_DIR / "backups")))
BACKUP_KEEP_DAYS = int(os.getenv("BACKUP_KEEP_DAYS", "14"))
BACKUP_PG_DUMP_PATH = os.getenv("BACKUP_PG_DUMP_PATH", "pg_dump")
BACKUP_SCHEDULE_HOUR = int(os.getenv("BACKUP_SCHEDULE_HOUR", "3"))
BACKUP_SCHEDULE_MINUTE = int(os.getenv("BACKUP_SCHEDULE_MINUTE", "0"))

if BACKUP_ENABLED:
    CELERY_BEAT_SCHEDULE["create_postgres_backup_daily"] = {
        "task": "core.tasks.create_postgres_backup",
        "schedule": crontab(hour=BACKUP_SCHEDULE_HOUR, minute=BACKUP_SCHEDULE_MINUTE),
    }

# ================= EMAIL =================

EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "true").lower() == "true"
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "TrackNode <noreply@tracknode.local>")

# ================= REPORTS =================

REPORTS_STORAGE_DIR = BASE_DIR / "reports_storage"

# ================= AI =================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL_SEO = os.getenv("OPENAI_MODEL_SEO", "gpt-5-mini").strip() or "gpt-5-mini"
OPENAI_MODEL_CONVERSION = os.getenv("OPENAI_MODEL_CONVERSION", "gpt-5-mini").strip() or "gpt-5-mini"
AI_RECOMMENDATIONS_ENABLED = os.getenv("AI_RECOMMENDATIONS_ENABLED", "false").lower() == "true"
AI_RECOMMENDATIONS_TIMEOUT_SECONDS = float(os.getenv("AI_RECOMMENDATIONS_TIMEOUT_SECONDS", "20"))
AI_RECOMMENDATIONS_TTL_SECONDS = int(os.getenv("AI_RECOMMENDATIONS_TTL_SECONDS", "10800"))
AI_RECOMMENDATIONS_MAX_OUTPUT_TOKENS = int(os.getenv("AI_RECOMMENDATIONS_MAX_OUTPUT_TOKENS", "900"))
AI_RECOMMENDATIONS_MAX_OUTPUT_TOKENS_SEO = int(
    os.getenv("AI_RECOMMENDATIONS_MAX_OUTPUT_TOKENS_SEO", "700")
)
AI_RECOMMENDATIONS_MAX_OUTPUT_TOKENS_CONVERSION = int(
    os.getenv("AI_RECOMMENDATIONS_MAX_OUTPUT_TOKENS_CONVERSION", str(AI_RECOMMENDATIONS_MAX_OUTPUT_TOKENS))
)
AI_RECOMMENDATIONS_MAX_OUTPUT_TOKENS_RETRY_CAP = int(
    os.getenv("AI_RECOMMENDATIONS_MAX_OUTPUT_TOKENS_RETRY_CAP", "1200")
)

# ================= LOGGING =================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "%(asctime)s %(levelname)s %(name)s %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "root": {"handlers": ["console"], "level": os.getenv("LOG_LEVEL", "INFO")},
    "loggers": {
        "analytics_app": {"handlers": ["console"], "level": os.getenv("LOG_LEVEL", "INFO"), "propagate": False},
        "leads": {"handlers": ["console"], "level": os.getenv("LOG_LEVEL", "INFO"), "propagate": False},
        "clients": {"handlers": ["console"], "level": os.getenv("LOG_LEVEL", "INFO"), "propagate": False},
        "tracker": {"handlers": ["console"], "level": os.getenv("LOG_LEVEL", "INFO"), "propagate": False},
        "telegram_logs": {"handlers": ["console"], "level": os.getenv("LOG_LEVEL", "INFO"), "propagate": False},
        "reports": {"handlers": ["console"], "level": os.getenv("LOG_LEVEL", "INFO"), "propagate": False},
    },
}

