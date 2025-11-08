from unittest import mock

from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase


class WebhookViewTests(APITestCase):
    def _post(self, payload: dict):
        return self.client.post(
            "/telegram/webhook/",
            data=payload,
            format="json",
        )

    def test_invalid_json_returns_400(self):
        response = self.client.post(
            "/telegram/webhook/",
            data="not-json",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_webhook_ignores_updates_without_text(self):
        payload = {"message": {"chat": {"id": 1}}}

        with mock.patch("core.views.telegram_client.send_message") as send_message:
            response = self._post(payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
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

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        pick_greeting.assert_called_once()
        send_message.assert_called_once_with(99, "Bonjour, Ariana!")

    def test_webhook_requires_chat_id(self):
        payload = {"message": {"text": "hola"}}

        with mock.patch("core.views.telegram_client.send_message") as send_message:
            response = self._post(payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        send_message.assert_not_called()

    @override_settings(TELEGRAM_BOT_TOKEN="")
    def test_webhook_skips_sending_when_token_missing(self):
        payload = {
            "message": {
                "chat": {"id": 5},
                "text": "Hi",
            }
        }

        with mock.patch("core.views.telegram_client.send_message") as send_message:
            response = self._post(payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        send_message.assert_not_called()

    @override_settings(TELEGRAM_BOT_TOKEN="secret-token")
    def test_webhook_handles_failed_send(self):
        payload = {
            "message": {
                "chat": {"id": 88},
                "text": "hello",
            }
        }

        with mock.patch("core.views.telegram_client.send_message", return_value=False) as send_message:
            response = self._post(payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        send_message.assert_called_once_with(88, mock.ANY)
