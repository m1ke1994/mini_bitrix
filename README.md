# Mini Bitrix SaaS MVP

Production-ready MVP SaaS:

- Backend: Django 4 + DRF + PostgreSQL + Redis + Celery + JWT
- Multi-tenant model via `Client` + unique `api_key`
- Public API for leads/events with `X-API-KEY`
- Private CRM/analytics API via JWT
- Frontend: Vue 3 + Vite + Pinia + Axios + Chart.js
- Dockerized services (`web`, `db`, `redis`, `worker`)

## Backend API

- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/refresh/`
- `POST /api/public/lead/` (`X-API-KEY`)
- `POST /api/public/event/` (`X-API-KEY`)
- `GET /api/leads/`
- `PATCH /api/leads/{id}/status/`
- `GET /api/analytics/summary/`
- `GET/PATCH /api/client/settings/`

## Run

1. Create env:
   - `cp .env.example .env`
   - `cp frontend/.env.example frontend/.env`
2. Build and run:
   - `docker-compose up --build`
3. Optional local backend commands:
   - `python manage.py migrate`
   - `python manage.py createsuperuser`

## Tests

Backend tests include:

- API-key validation for public lead endpoint
- Lead creation for valid API-key

Run tests inside backend container:

- `python manage.py test`

## Localization (RU)

Проект локализован для русского языка:

- `LANGUAGE_CODE = "ru"`
- `TIME_ZONE = "Europe/Moscow"`
- `LocaleMiddleware` включен
- `LOCALE_PATHS = [BASE_DIR / "locale"]`

Сборка переводов внутри Docker:

- `docker-compose exec web python manage.py makemessages -l ru`
- `docker-compose exec web python manage.py compilemessages`

## Frontend

Frontend now starts with `docker-compose up --build` (service `frontend` on `http://localhost:9003`).

## External Website Integration

See `CONNECT.md` for lead/event integration examples.
