from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from core.telegram import TelegramClient


class Command(BaseCommand):
    help = "Register the Telegram webhook URL with Telegram."

    def add_arguments(self, parser):
        parser.add_argument(
            "--url",
            dest="url",
            help="Public HTTPS URL for the webhook (defaults to TELEGRAM_WEBHOOK_URL setting).",
        )

    def handle(self, *args, **options):
        url = options.get("url") or settings.TELEGRAM_WEBHOOK_URL
        if not url:
            raise CommandError("Provide --url or set TELEGRAM_WEBHOOK_URL in your environment.")

        if not settings.TELEGRAM_BOT_TOKEN:
            raise CommandError("TELEGRAM_BOT_TOKEN is missing; set it before registering the webhook.")

        client = TelegramClient(token=settings.TELEGRAM_BOT_TOKEN)

        if not client.set_webhook(url, secret_token=settings.TELEGRAM_WEBHOOK_SECRET or None):
            raise CommandError(f"Failed to register webhook with Telegram using URL {url}")

        self.stdout.write(self.style.SUCCESS(f"Webhook successfully set to {url}"))
