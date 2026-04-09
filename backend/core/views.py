from __future__ import annotations

import logging

from django.conf import settings
from django.core.cache import caches
from django.db import connection
from django.http import JsonResponse
from django.utils import timezone

from saas_platform.celery import app as celery_app

logger = logging.getLogger(__name__)


def _check_database() -> dict:
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            row = cursor.fetchone()
        return {"status": "ok", "result": int(row[0]) if row else 1}
    except Exception as exc:
        logger.exception("Healthcheck database probe failed")
        return {"status": "error", "error": str(exc)}


def _check_redis() -> dict:
    try:
        cache = caches["default"]
        key = "healthcheck:ping"
        value = timezone.now().isoformat()
        cache.set(key, value, timeout=10)
        cached = cache.get(key)
        if cached != value:
            return {"status": "error", "error": "cache read/write mismatch"}
        return {"status": "ok"}
    except Exception as exc:
        logger.exception("Healthcheck redis probe failed")
        return {"status": "error", "error": str(exc)}


def _check_celery() -> dict:
    if not settings.HEALTHCHECK_CELERY_PING_ENABLED:
        return {"status": "skipped", "detail": "disabled"}
    try:
        result = celery_app.control.ping(timeout=settings.HEALTHCHECK_CELERY_PING_TIMEOUT_SECONDS)
        workers = [list(item.keys())[0] for item in (result or []) if isinstance(item, dict) and item]
        if workers:
            return {"status": "ok", "workers": workers}
        return {"status": "degraded", "workers": []}
    except Exception as exc:
        logger.exception("Healthcheck celery probe failed")
        return {"status": "error", "error": str(exc)}


def health_view(request):
    checks = {
        "database": _check_database(),
        "redis": _check_redis(),
        "celery": _check_celery(),
    }

    status_value = "ok"
    failing = [name for name, data in checks.items() if data.get("status") == "error"]
    if failing:
        status_value = "error"
    elif settings.HEALTHCHECK_REQUIRE_CELERY and checks["celery"].get("status") not in {"ok", "skipped"}:
        status_value = "degraded"

    is_ok = status_value == "ok"
    return JsonResponse(
        {
            "status": status_value,
            "timestamp": timezone.now().isoformat(),
            "checks": checks,
        },
        status=200 if is_ok else 503,
    )


def custom_404(request, exception):
    return JsonResponse({"error": "Страница не найдена"}, status=404)

