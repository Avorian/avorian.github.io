import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ella_prototype import EllaChatbot


def test_greeting_intent_response():
    bot = EllaChatbot()
    reply = bot.respond("Hello there")
    assert "friendly assistant" in reply


def test_productivity_knowledge_response():
    bot = EllaChatbot()
    reply = bot.respond("I need help staying productive at work")
    assert "Staying productive" in reply
    assert "What kind of work" in reply


def test_custom_response_is_used():
    bot = EllaChatbot()
    bot.add_custom_response("favorite color", "Teal is my favorite shade!", "Do you like it too?")
    reply = bot.respond("What's your favorite color?")
    assert "Teal is my favorite shade" in reply
    assert "Do you like it too?" in reply


def test_blank_message_prompts_user():
    bot = EllaChatbot()
    reply = bot.respond("   ")
    assert "whenever you're ready" in reply


def test_conversation_history_records_dialogue():
    bot = EllaChatbot()
    bot.respond("Hey Ella")
    bot.respond("Tell me about your wellbeing tips")
    assert len(bot.conversation_history) == 2
    assert bot.conversation_history[0]["user"] == "Hey Ella"
    assert "wellbeing" in bot.conversation_history[1]["ella"].lower()
