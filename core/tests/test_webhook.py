from unittest import mock

from django.conf import settings
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase


class WebhookViewTests(APITestCase):
    _DEFAULT_SECRET = object()
    DEFAULT_SECRET_VALUE = "dummy-test-secret"

    def setUp(self):
        super().setUp()
        self._secret_override = override_settings(TELEGRAM_WEBHOOK_SECRET=self.DEFAULT_SECRET_VALUE)
        self._secret_override.enable()

    def tearDown(self):
        self._secret_override.disable()
        super().tearDown()

    def _post(self, payload: dict, secret=_DEFAULT_SECRET):
        path = "/telegram/webhook/"
        resolved_secret = secret
        if secret is self._DEFAULT_SECRET:
            resolved_secret = settings.TELEGRAM_WEBHOOK_SECRET
        headers = {}
        if resolved_secret is not None and resolved_secret != "":
            headers["HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN"] = resolved_secret
        return self.client.post(path, data=payload, format="json", **headers)

    def test_invalid_json_returns_400(self):
        response = self.client.post(
            "/telegram/webhook/",
            data="not-json",
            content_type="application/json",
            HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN=self.DEFAULT_SECRET_VALUE,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_webhook_ignores_updates_without_message_payload(self):
        payload = {"callback_query": {"data": "noop"}}

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

    @override_settings(TELEGRAM_BOT_TOKEN="secret-token")
    def test_webhook_replies_to_non_text_messages(self):
        payload = {
            "message": {
                "chat": {"id": 42},
                "sticker": {"emoji": "🎉"},
            }
        }

        with mock.patch("core.views.pick_greeting", return_value="Hey there!") as pick_greeting, mock.patch(
            "core.views.telegram_client.send_message", return_value=True
        ) as send_message:
            response = self._post(payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        pick_greeting.assert_called_once()
        send_message.assert_called_once_with(42, "Hey there!")

    @override_settings(TELEGRAM_WEBHOOK_SECRET="topsecret")
    def test_webhook_rejects_missing_secret(self):
        payload = {"message": {"chat": {"id": 11}, "text": "hello"}}

        with mock.patch("core.views.telegram_client.send_message") as send_message:
            response = self._post(payload, secret=None)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        send_message.assert_not_called()

    @override_settings(TELEGRAM_WEBHOOK_SECRET="topsecret")
    def test_webhook_rejects_invalid_secret(self):
        payload = {"message": {"chat": {"id": 11}, "text": "hello"}}

        with mock.patch("core.views.telegram_client.send_message") as send_message:
            response = self._post(payload, secret="wrong")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        send_message.assert_not_called()

    @override_settings(TELEGRAM_BOT_TOKEN="secret-token", TELEGRAM_WEBHOOK_SECRET="topsecret")
    def test_webhook_accepts_valid_secret(self):
        payload = {
            "message": {
                "chat": {"id": 77},
                "text": "hey",
            }
        }

        with mock.patch("core.views.telegram_client.send_message", return_value=True) as send_message:
            response = self._post(payload, secret="topsecret")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        send_message.assert_called_once_with(77, mock.ANY)

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
