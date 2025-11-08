import random
from typing import Optional

GREETINGS = ("Hello", "Hola", "Bonjour")


def extract_sender_name(message: Optional[dict]) -> str:
    """
    Pull the most friendly sender name we can find from the Telegram message.
    """
    if not isinstance(message, dict):
        return "there"

    sender = message.get("from") or {}
    name = (
        sender.get("first_name")
        or sender.get("username")
        or sender.get("last_name")
        or sender.get("language_code")
    )
    return name or "there"


def pick_greeting(name: Optional[str] = None, *, rng: Optional[random.Random] = None) -> str:
    """
    Return a greeting in a randomly selected language, addressing the sender.
    """
    selector = rng or random
    chosen = selector.choice(GREETINGS)
    safe_name = name or "there"
    return f"{chosen}, {safe_name}!"
