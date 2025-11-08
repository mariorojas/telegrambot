import json
import logging

from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .helpers import extract_sender_name, pick_greeting
from .telegram import TelegramClient

logger = logging.getLogger(__name__)
telegram_client = TelegramClient()


@method_decorator(csrf_exempt, name="dispatch")
class WebhookView(View):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        try:
            payload = json.loads(request.body or "{}")
        except json.JSONDecodeError:
            logger.warning("Received invalid JSON payload from Telegram.")
            return HttpResponse(status=400)

        message = payload.get("message") or payload.get("edited_message")
        if not isinstance(message, dict) or "text" not in message:
            logger.debug("Ignoring update without text message: %s", payload.get("update_id"))
            return HttpResponse(status=200)

        chat = message.get("chat") or {}
        chat_id = chat.get("id")
        if chat_id is None:
            logger.warning("Received message without chat id: %s", message)
            return HttpResponse(status=200)

        greeting = pick_greeting(extract_sender_name(message))

        if not settings.TELEGRAM_BOT_TOKEN:
            logger.error("TELEGRAM_BOT_TOKEN is not configured; cannot respond.")
            return HttpResponse(status=200)

        if not telegram_client.send_message(chat_id, greeting):
            logger.error("Failed to send greeting to chat %s", chat_id)
        else:
            logger.info("Greeting sent to chat %s: %s", chat_id, greeting)
        return HttpResponse(status=200)
