import logging
from typing import Any, Dict, Optional

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class TelegramClient:
    api_base = "https://api.telegram.org"

    def __init__(self, token: Optional[str] = None):
        self.token = token or settings.TELEGRAM_BOT_TOKEN

    def _build_url(self, method: str) -> str:
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN is not configured.")
        return f"{self.api_base}/bot{self.token}/{method}"

    def _post(self, method: str, payload: Dict[str, Any]) -> bool:
        try:
            response = requests.post(
                self._build_url(method),
                json=payload,
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
        except Exception:
            logger.exception("Telegram API request failed for method %s", method)
            return False

        if not data.get("ok"):
            logger.error("Telegram API responded with failure: %s", data)
            return False
        return True

    def send_message(self, chat_id: int | str, text: str) -> bool:
        return self._post(
            "sendMessage",
            {
                "chat_id": chat_id,
                "text": text,
            },
        )

    def set_webhook(self, url: str) -> bool:
        return self._post(
            "setWebhook",
            {
                "url": url,
            },
        )
