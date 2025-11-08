from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

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

        token = settings.TELEGRAM_BOT_TOKEN
        if not token:
            raise CommandError("TELEGRAM_BOT_TOKEN is missing; set it before registering the webhook.")

        secret = getattr(settings, "TELEGRAM_WEBHOOK_SECRET", "")
        url_with_secret = self._append_secret(url, secret) if secret else url

        client = TelegramClient(token=token)
        if not client.set_webhook(url_with_secret):
            raise CommandError(f"Failed to register webhook with Telegram using URL {url_with_secret}")

        self.stdout.write(self.style.SUCCESS(f"Webhook successfully set to {url_with_secret}"))

    @staticmethod
    def _append_secret(url: str, secret: str) -> str:
        parsed = urlparse(url)
        query_params = dict(parse_qsl(parsed.query, keep_blank_values=True))
        query_params["secret"] = secret
        new_query = urlencode(query_params, doseq=True)
        return urlunparse(parsed._replace(query=new_query))
