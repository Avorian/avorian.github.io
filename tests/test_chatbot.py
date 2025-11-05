import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ella_prototype import CommandRouter, EllaChatbot


@pytest.fixture()
def bot() -> EllaChatbot:
    return EllaChatbot()


def test_greeting_triggers_emotional_follow_up(bot: EllaChatbot) -> None:
    payload = bot.respond_rich("Hello Ella")
    assert "lovely to hear from you" in payload.message.lower()
    assert payload.follow_up == "Is there something on your heart that you'd like to explore together?"
    assert payload.emotion in {"calm", "encouraging", "radiant", "soothing", "concerned"}


def test_productivity_topic_includes_follow_up(bot: EllaChatbot) -> None:
    payload = bot.respond_rich("I need help staying productive at work")
    assert "staying productive thrives on gentle rituals" in payload.message.lower()
    assert payload.follow_up == "What project deserves your fullest attention right now?"


def test_custom_response_keeps_follow_up(bot: EllaChatbot) -> None:
    bot.add_custom_response("favorite color", "Teal is my favorite shade!", "Do you like it too?")
    payload = bot.respond_rich("What's your favorite color?")
    assert "teal is my favorite shade" in payload.message.lower()
    assert payload.follow_up == "Do you like it too?"


def test_blank_message_provides_comforting_space(bot: EllaChatbot) -> None:
    payload = bot.respond_rich("   ")
    assert "sitting with you in the quiet" in payload.message.lower()
    assert payload.follow_up is None


def test_conversation_history_captures_multimodal_entries(bot: EllaChatbot) -> None:
    bot.respond_rich("Hi Ella")
    bot.respond_rich("Tell me about your wellbeing rituals")
    assert len(bot.conversation_history) == 2
    assert bot.conversation_history[0]["user"] == "Hi Ella"
    assert "breath" in bot.conversation_history[1]["ella"].lower()


def test_image_generation_command(bot: EllaChatbot) -> None:
    payload = bot.respond_rich("Can you draw a sunrise over the ocean?")
    assert payload.attachments, "Expected an image attachment"
    image_asset = payload.attachments[0]
    assert image_asset["type"] == "image"
    assert "sunrise" in image_asset["prompt"].lower()
    assert image_asset["uri"].startswith("ella://image/")


def test_video_generation_command(bot: EllaChatbot) -> None:
    payload = bot.respond_rich("Please make a video about growth and resilience")
    assert payload.attachments, "Expected a video attachment"
    video_asset = next(asset for asset in payload.attachments if asset["type"] == "video")
    assert video_asset["duration"] >= 3
    assert video_asset["uri"].startswith("ella://video/")


def test_voice_mode_returns_audio_metadata(bot: EllaChatbot) -> None:
    payload = bot.respond_rich("Could you speak in voice mode about creativity?")
    assert payload.voice_data is not None
    assert payload.voice_data["voice"] == "warm alto"
    assert payload.voice_data["sample_uri"].startswith("ella://voice/")


def test_command_router_rejects_duplicates() -> None:
    router = CommandRouter()
    router.register("ping", lambda: {"ok": True})
    with pytest.raises(ValueError):
        router.register("ping", lambda: {"ok": True})


def test_command_router_missing_command() -> None:
    router = CommandRouter()
    with pytest.raises(KeyError):
        router.execute("unknown")
