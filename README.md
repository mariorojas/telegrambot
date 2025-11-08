# Telegram Webhook Bot

This Django project exposes a webhook endpoint that receives Telegram updates and responds with a randomly selected greeting in English, Spanish, or French.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure the environment (create a `.env` file in the project root):
   ```
   TELEGRAM_BOT_TOKEN=your-bot-token
   TELEGRAM_WEBHOOK_URL=https://public-host/telegram/webhook/  # optional
   TELEGRAM_WEBHOOK_SECRET=some-long-random-string            # optional but recommended
   DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,beribboned-vickey-metrically.ngrok-free.dev
   ```
   These values are loaded automatically via `python-dotenv`. You can still override them with standard environment variables.

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
