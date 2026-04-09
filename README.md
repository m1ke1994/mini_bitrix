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
If PWA icons/manifest do not refresh, open DevTools -> Application -> Service Workers -> `Unregister`, then hard reload.
Also clear Application -> Storage -> `Clear site data` for a full icon/cache reset.

## External Website Integration

See `CONNECT.md` for lead/event integration examples.
