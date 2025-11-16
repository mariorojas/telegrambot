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
    name = next(
        (sender.get(key) for key in ("first_name", "username", "last_name", "language_code") if sender.get(key)),
        None,
    )
    return name or "there"


def pick_greeting(name: Optional[str] = None, *, rng: Optional[random.Random] = None) -> str:
    """
    Return a greeting in a randomly selected language, addressing the sender.
    """
    chosen = (rng or random).choice(GREETINGS)
    return f"{chosen}, {name or 'there'}!"
