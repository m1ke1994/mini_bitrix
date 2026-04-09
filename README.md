# Mini Bitrix / TrackNode

Production-minded SaaS CRM for lead capture, behavior tracking, analytics, and conversion growth.

## Stack

- Backend: Django 4, DRF, PostgreSQL, Redis, Celery, JWT, Channels
- Frontend: Nuxt 3, Vue 3, Pinia, Chart.js, vuedraggable
- Infra: Docker Compose (`web-init`, `web`, `ws`, `worker`, `beat`, `frontend`, `db`, `redis`)
- Integrations: Telegram, webhook, email, OpenAI API

## Security and Infra Updates

- `DJANGO_SECRET_KEY` is mandatory (container startup fails if missing).
- PostgreSQL and Redis are internal-only in main `docker-compose.yml`.
- Optional dev exposure is available in `docker-compose.dev.yml`.
- Migrations/static collection are split from app startup via `web-init` service.
- Health endpoint: `GET /api/health/` (database, redis, celery ping).
- Public API throttling enabled via DRF scoped throttles.

## Quick Start

1. Create env file:
   - `cp .env.example .env`
2. Set required value:
   - `DJANGO_SECRET_KEY` (must be non-empty and long random)
3. Start services:
   - `docker compose up --build`
4. Open:
   - Backend: `http://localhost:9000`
   - Frontend: `http://localhost:9003`
   - WebSocket: `ws://localhost:9010/ws/leads/`

### Dev Mode With Exposed DB/Redis

Use override file:

- `docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build`

This exposes:

- PostgreSQL: `localhost:9001`
- Redis: `localhost:9002`

## Main Backend Endpoints

### Auth

- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/logout/`
- `POST /api/auth/refresh/`

### Public

- `POST /api/public/lead/` (`X-API-KEY`)
- `POST /api/public/event/` (`X-API-KEY`)
- `POST /api/analytics/event/` (`X-API-KEY`)
- `GET /api/public/widget/variant/` (`X-API-KEY`)
- `POST /api/public/widget/impression/` (`X-API-KEY`)

### CRM

- `GET /api/pipelines/`
- `GET /api/leads/`
- `GET /api/leads/{id}/`
- `PATCH /api/leads/{id}/status/` (backward-compatible)
- `POST /api/leads/{id}/move/`
- `GET /api/leads/{id}/activities/`
- `POST /api/leads/{id}/note/`
- `POST /api/leads/{id}/schedule/`
- `GET/POST/PATCH/DELETE /api/widget-variants/`

### Analytics

- `GET /api/analytics/overview/`
- `GET /api/analytics/summary/`
- `GET /api/analytics/funnel/`
- `GET /api/analytics/sources/`
- `GET /api/analytics/timeline/`
- `GET /api/analytics/response-time/`
- `GET /api/analytics/conversion-rate/`
- `GET /api/analytics/heatmap/`
- `GET /api/analytics/ai-advisor/`
- `GET /api/analytics/ai-recommendations/`

### Platform

- `GET /api/health/`
- `GET /tracker.js`
- `GET /widget.js`

<<<<<<< HEAD
## Ollama Local AI Provider

This project supports two AI providers for recommendations:

- `ollama` (default)
- `openai`

### Start with Docker Compose

1. Ensure `.env` contains:
   - `AI_PROVIDER=ollama`
   - `OLLAMA_BASE_URL=http://ollama:11434`
   - `OLLAMA_MODEL_SEO=qwen2.5:7b`
   - `OLLAMA_MODEL_CONVERSION=qwen2.5:7b`
2. Start services:
   - `docker compose up -d --build`
3. Check Ollama availability:
   - `curl http://localhost:11434/api/tags`

### Pull `qwen2.5:7b`

Models are pulled by one-time `ollama_init` service automatically.
You can also pull manually:

- `docker compose exec ollama ollama pull qwen2.5:7b`

### Warm Up Model

Warm up configured Ollama models from the Django container:

- `docker compose exec web python manage.py warmup_ollama`

### Switch Provider

- Use Ollama:
  - `AI_PROVIDER=ollama`
- Use OpenAI:
  - `AI_PROVIDER=openai`
  - `OPENAI_API_KEY=<your_key>`

### Common Issues

- Model is not downloaded:
  - run `docker compose logs -f ollama_init` and `docker compose exec ollama ollama list`
- First response is slow:
  - this is expected on first load; run warmup command to preload models
- Not enough RAM:
  - use a smaller model or increase Docker memory limit
- Timeout errors:
  - increase `OLLAMA_REQUEST_TIMEOUT_SECONDS`
- Ollama service is unavailable:
  - verify `OLLAMA_BASE_URL`, service name `ollama`, and `docker compose logs -f ollama`

## Tests
=======
## Frontend Additions
>>>>>>> c49e52d863c20cba3901447a483ff75db2d8a736

- `GET /app/crm` - CRM Kanban board with drag-and-drop and realtime updates.
- `GET /app/crm/analytics` - CRM dashboard for funnel/sources/timeline/conversion/heatmap/AI advisor.

## Tracker and Widget Integration

See `CONNECT.md` for examples.

## Realtime

- Backend consumer: `ws://<host>/ws/leads/?token=<JWT_ACCESS_TOKEN>`
- Events are client-isolated via tenant-scoped channel groups.

## Lead Processing Features

- Pipeline/stage model with default bootstrap.
- Lead activity timeline (`LeadActivity`).
- Deduplication by normalized phone/email (merge strategy by default).
- Automatic lead scoring (0..100).
- Notification tasks: Telegram/email/webhook.
- Stale lead reminders.
- Auto response by client settings (email path implemented).

## Backup Scaffold

- Celery task: `core.tasks.create_postgres_backup`
- Controlled by env:
  - `BACKUP_ENABLED=true`
  - schedule: `BACKUP_SCHEDULE_HOUR`, `BACKUP_SCHEDULE_MINUTE`
  - retention: `BACKUP_KEEP_DAYS`

## Useful Commands

- Backend checks:
  - `python backend/manage.py check`
- Recalculate scores:
  - `python backend/manage.py recalculate_lead_scores`
- Build frontend:
  - `cd frontend && npm run build`

## Notes

- Existing `seo_audit` migration drift (if present in your branch) is unrelated to CRM roadmap changes.
- Existing status endpoint is kept for backward compatibility.
