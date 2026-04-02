#!/usr/bin/env sh
set -eu

if [ -z "${DJANGO_SECRET_KEY:-}" ]; then
  echo "ERROR: DJANGO_SECRET_KEY is required." >&2
  exit 1
fi

export SECRET_KEY="${SECRET_KEY:-$DJANGO_SECRET_KEY}"

command_name="${1:-web}"
shift || true

case "$command_name" in
  migrate_collectstatic)
    python manage.py migrate --noinput
    python manage.py collectstatic --noinput
    ;;
  web)
    exec gunicorn saas_platform.wsgi:application --bind 0.0.0.0:8000
    ;;
  websocket)
    exec daphne -b 0.0.0.0 -p 8010 saas_platform.asgi:application
    ;;
  worker)
    exec celery -A saas_platform worker -l info
    ;;
  beat)
    exec celery -A saas_platform beat -l info
    ;;
  telegram_poller)
    exec python manage.py run_telegram_polling
    ;;
  *)
    exec "$command_name" "$@"
    ;;
esac
