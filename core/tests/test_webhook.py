import json
from unittest import mock

from django.test import Client, TestCase, override_settings


class WebhookViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def _post(self, payload: dict):
        return self.client.post(
            "/telegram/webhook/",
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_webhook_ignores_updates_without_text(self):
        payload = {"message": {"chat": {"id": 1}}}

        with mock.patch("core.views.telegram_client.send_message") as send_message:
            response = self._post(payload)

        self.assertEqual(response.status_code, 200)
        send_message.assert_not_called()

    @override_settings(TELEGRAM_BOT_TOKEN="secret-token")
    def test_webhook_replies_to_text_messages(self):
        payload = {
            "message": {
                "chat": {"id": 99},
                "text": "hi bot",
                "from": {"first_name": "Ariana"},
            }
        }

        with mock.patch("core.views.pick_greeting", return_value="Bonjour, Ariana!") as pick_greeting, mock.patch(
            "core.views.telegram_client.send_message", return_value=True
        ) as send_message:
            response = self._post(payload)

        self.assertEqual(response.status_code, 200)
        pick_greeting.assert_called_once()
        send_message.assert_called_once_with(99, "Bonjour, Ariana!")
