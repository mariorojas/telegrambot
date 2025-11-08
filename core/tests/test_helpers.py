import random

from core import helpers


def test_extract_sender_name_prefers_first_name():
    message = {"from": {"first_name": "Pat", "username": "pat123"}}
    assert helpers.extract_sender_name(message) == "Pat"


def test_extract_sender_name_falls_back_to_username():
    message = {"from": {"username": "botfan"}}
    assert helpers.extract_sender_name(message) == "botfan"


def test_pick_greeting_uses_rng_and_formats_name():
    rng = random.Random(0)
    greeting = helpers.pick_greeting("Sam", rng=rng)
    assert greeting == "Hola, Sam!"


def test_pick_greeting_defaults_name_when_missing():
    rng = random.Random(1)
    greeting = helpers.pick_greeting(None, rng=rng)
    assert greeting.endswith(", there!")
