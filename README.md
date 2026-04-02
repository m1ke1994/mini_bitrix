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

## Frontend Additions

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
