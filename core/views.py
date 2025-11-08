import logging
from typing import Any, Dict, Optional

from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import ParseError
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .helpers import extract_sender_name, pick_greeting
from .telegram import TelegramClient

logger = logging.getLogger(__name__)
telegram_client = TelegramClient()

Payload = Dict[str, Any]
Message = Dict[str, Any]


class WebhookView(APIView):
    authentication_classes = []
    permission_classes = []
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        if not self._is_authorized(request):
            logger.warning("Rejected webhook call due to missing/invalid secret.")
            return Response(status=status.HTTP_403_FORBIDDEN)

        try:
            payload: Payload = request.data or {}
        except ParseError:
            logger.warning("Received invalid JSON payload from Telegram.")
            return Response(status=status.HTTP_400_BAD_REQUEST)

        message = self._extract_text_message(payload)
        if not message:
            logger.debug("Ignoring update without text message: %s", payload.get("update_id"))
            return Response(status=status.HTTP_200_OK)

        chat_id = self._get_chat_id(message)
        if chat_id is None:
            logger.warning("Received message without chat id: %s", message)
            return Response(status=status.HTTP_200_OK)

        greeting = self._prepare_greeting(message)
        if self._send_greeting(chat_id, greeting):
            logger.info("Greeting sent to chat %s: %s", chat_id, greeting)
        else:
            logger.error("Failed to send greeting to chat %s", chat_id)
        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def _extract_text_message(payload: Payload) -> Optional[Message]:
        if not isinstance(payload, dict):
            return None

        message = payload.get("message") or payload.get("edited_message")
        if isinstance(message, dict) and isinstance(message.get("text"), str):
            return message
        return None

    @staticmethod
    def _get_chat_id(message: Message) -> Optional[int]:
        chat = message.get("chat")
        if isinstance(chat, dict):
            return chat.get("id")
        return None

    @staticmethod
    def _prepare_greeting(message: Message) -> str:
        return pick_greeting(extract_sender_name(message))

    @staticmethod
    def _send_greeting(chat_id: int, greeting: str) -> bool:
        if not settings.TELEGRAM_BOT_TOKEN:
            logger.error("TELEGRAM_BOT_TOKEN is not configured; cannot respond.")
            return False
        return telegram_client.send_message(chat_id, greeting)

    @staticmethod
    def _is_authorized(request) -> bool:
        secret = getattr(settings, "TELEGRAM_WEBHOOK_SECRET", "")
        if not secret:
            return True
        return request.query_params.get("secret") == secret
