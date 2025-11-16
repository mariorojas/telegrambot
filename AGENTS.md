# Repository Guidelines

## Project Structure & Module Organization
- `core/` – app logic: `views.py` (webhook handling), `helpers.py` (greeting utilities), `telegram.py` (API client), management command `management/commands/setwebhook.py`.
- `telegrambot/` – Django project settings, URLs, WSGI entrypoint.
- `core/tests/` – unit and API tests for views, helpers, and management commands.
- Top level: `manage.py` (Django runner), `requirements.txt`, `env.example`.

## Build, Test, and Development Commands
- Create venv & install deps: `python -m venv venv && source venv/bin/activate && pip install -r requirements.txt`.
- Run tests: `source venv/bin/activate && python manage.py test`.
- Local server: `source venv/bin/activate && python manage.py runserver` (uses settings in `telegrambot/settings.py`; ensure env vars are set).
- Set webhook (reqs network): `python manage.py setwebhook --url https://yourdomain/telegram/webhook/`.

## Coding Style & Naming Conventions
- Python 3.13; follow PEP 8, 4-space indentation.
- Django settings read via `django.conf.settings` attributes (no `getattr` fallbacks).
- Functions and variables: `snake_case`; classes: `CamelCase`.
- Prefer early returns and concise expressions; log via module-level `logger`.
- Default to class-based views over function-based ones; keep implementations idiomatic/pythonic.

## Testing Guidelines
- Frameworks: `django.test`, `rest_framework.test`, `unittest.mock`.
- Test files live in `core/tests/`; name tests `test_*.py` with readable method names.
- Keep webhook tests isolated using `override_settings` and mocks for network calls; avoid hitting real Telegram API.
- Always run `python manage.py test` before pushing.

## Commit & Pull Request Guidelines
- Commit messages: concise imperative (“Add webhook secret check”); group related changes per commit.
- Pull requests should include: summary of changes, test evidence (command + status), and any config/env considerations (e.g., new settings).

## Security & Configuration Tips
- Required env vars: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_URL`, optional `TELEGRAM_WEBHOOK_SECRET`; copy `env.example` to `.env`.
- In DEBUG, missing webhook secret allows calls; in production, set a strong `TELEGRAM_WEBHOOK_SECRET`.
- Do not check secrets into VCS; keep `.env` out of version control.
