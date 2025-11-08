from unittest import mock

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings


class SetWebhookCommandTests(TestCase):
    def _call(self, *, url="https://example.com/hook", secret="s3cr3t"):
        with override_settings(
            TELEGRAM_WEBHOOK_URL=url,
            TELEGRAM_WEBHOOK_SECRET=secret,
            TELEGRAM_BOT_TOKEN="token",
        ):
            with mock.patch("core.management.commands.setwebhook.TelegramClient") as client_cls:
                client_instance = client_cls.return_value
                client_instance.set_webhook.return_value = True
                call_command("setwebhook")
        return client_instance.set_webhook.call_args[0][0]

    def test_appends_secret_to_url_without_query(self):
        result_url = self._call(url="https://example.com/hook", secret="topsecret")
        self.assertEqual(result_url, "https://example.com/hook?secret=topsecret")

    def test_appends_secret_to_url_with_existing_query(self):
        result_url = self._call(url="https://example.com/hook?foo=bar", secret="topsecret")
        self.assertEqual(result_url, "https://example.com/hook?foo=bar&secret=topsecret")

    def test_uses_plain_url_when_secret_missing(self):
        with override_settings(
            TELEGRAM_WEBHOOK_URL="https://example.com/hook",
            TELEGRAM_WEBHOOK_SECRET="",
            TELEGRAM_BOT_TOKEN="token",
        ):
            with mock.patch("core.management.commands.setwebhook.TelegramClient") as client_cls:
                client_instance = client_cls.return_value
                client_instance.set_webhook.return_value = True
                call_command("setwebhook")

        client_cls.return_value.set_webhook.assert_called_once_with("https://example.com/hook")

    def test_raises_when_webhook_registration_fails(self):
        with override_settings(
            TELEGRAM_WEBHOOK_URL="https://example.com/hook",
            TELEGRAM_WEBHOOK_SECRET="secret",
            TELEGRAM_BOT_TOKEN="token",
        ):
            with mock.patch("core.management.commands.setwebhook.TelegramClient") as client_cls:
                client_cls.return_value.set_webhook.return_value = False
                with self.assertRaises(CommandError):
                    call_command("setwebhook")
