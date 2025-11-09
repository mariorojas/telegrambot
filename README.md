# Telegram Webhook Bot

This Django project exposes a webhook endpoint that receives Telegram updates and responds with a randomly selected greeting in English, Spanish, or French.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure your environment variables:
   - Rename `env.example` to `.env` by executing `mv env.example .env`.
   - Replace the placeholder values with your bot token, webhook URL (if any), and optional webhook secret, allowed hosts, etc.
   - The project automatically loads `.env` via `python-dotenv`, but you can still override values using standard environment variables.

## Running Locally

1. Start Django:
   ```bash
   python manage.py runserver
   ```
2. Expose the webhook publicly (e.g., `ngrok http 8000`) and note the HTTPS URL, such as `https://your-id.ngrok.app/telegram/webhook/`.

## Register the Webhook

Run the provided management command once your public URL is ready:
```bash
python manage.py setwebhook --url https://your-id.ngrok.app/telegram/webhook/
```
If `TELEGRAM_WEBHOOK_URL` is set, you can omit `--url`.

When `TELEGRAM_WEBHOOK_SECRET` is defined, the management command automatically appends `?secret=<value>` (or `&secret=` if other query params exist) to the URL sent to Telegram. Telegram will then include that query parameter in every webhook request, and the Django view will reject requests without the correct secret.

## Testing

Execute the Django test suite:
```bash
python manage.py test
```
