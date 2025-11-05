"""Core implementation of the Ella Prototype chatbot with immersive features."""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha1
from typing import Callable, Dict, Iterable, List, Optional


# ---------------------------------------------------------------------------
# Support infrastructure
# ---------------------------------------------------------------------------


class CommandRouter:
    """Simple command router that guarantees commands resolve reliably."""

    def __init__(self) -> None:
        self._commands: Dict[str, Callable[..., dict]] = {}

    def register(self, name: str, handler: Callable[..., dict], description: str = "") -> None:
        key = name.strip().lower()
        if not key:
            raise ValueError("Command name cannot be empty.")
        if key in self._commands:
            raise ValueError(f"Command '{name}' is already registered.")
        self._commands[key] = handler

    def execute(self, name: str, **payload: str) -> dict:
        key = name.strip().lower()
        if key not in self._commands:
            raise KeyError(f"Command '{name}' is not registered.")
        return self._commands[key](**payload)

    def list_commands(self) -> List[str]:
        return sorted(self._commands)


class CreativeEngine:
    """Generates structured placeholders for imagery and video."""

    def _stable_uri(self, seed: str, asset_type: str) -> str:
        digest = sha1(seed.encode("utf-8")).hexdigest()[:12]
        return f"ella://{asset_type}/{digest}"

    def generate_image(self, prompt: str, style: str = "dreamy") -> dict:
        prompt = prompt.strip() or "imaginative abstract"
        uri = self._stable_uri(f"image::{prompt}::{style}", "image")
        return {
            "type": "image",
            "prompt": prompt,
            "style": style,
            "uri": uri,
            "preview": f"A {style} depiction of {prompt}.",
        }

    def generate_video(self, prompt: str, duration: int = 6, mood: str = "hopeful") -> dict:
        prompt = prompt.strip() or "shifting colors"
        duration = max(3, min(duration, 30))
        uri = self._stable_uri(f"video::{prompt}::{duration}::{mood}", "video")
        return {
            "type": "video",
            "prompt": prompt,
            "duration": duration,
            "mood": mood,
            "uri": uri,
            "preview": f"{duration}s cinematic loop evoking {mood} vibes around {prompt}.",
        }


class VoiceEngine:
    """Simulates expressive voice synthesis for Ella's spoken mode."""

    def __init__(self, voice: str = "warm alto", base_speed: float = 1.0) -> None:
        self.voice = voice
        self.base_speed = base_speed

    def synthesize(self, text: str, emotion: str, tempo: float = 1.0) -> dict:
        if not text.strip():
            raise ValueError("Voice synthesis requires non-empty text.")
        tempo = max(0.6, min(self.base_speed * tempo, 1.6))
        digest = sha1(f"voice::{text}::{emotion}::{tempo}".encode("utf-8")).hexdigest()[:10]
        return {
            "voice": self.voice,
            "emotion": emotion,
            "tempo": round(tempo, 2),
            "sample_uri": f"ella://voice/{digest}",
        }


@dataclass
class EmotionState:
    """Tracks the chatbot's internal emotional landscape."""

    mood: float = 0.1
    energy: float = 0.6
    last_emotion: str = "calm"

    POSITIVE_MARKERS = {"love", "happy", "grateful", "excited", "great", "awesome"}
    NEGATIVE_MARKERS = {"sad", "tired", "stressed", "upset", "angry", "frustrated", "lonely"}

    def update(self, normalized: str) -> None:
        delta = 0.0
        if any(token in normalized for token in self.POSITIVE_MARKERS):
            delta += 0.15
        if any(token in normalized for token in self.NEGATIVE_MARKERS):
            delta -= 0.2
        if "thank" in normalized:
            delta += 0.08
        if "sorry" in normalized:
            delta -= 0.05

        self.mood = max(-1.0, min(1.0, self.mood + delta))
        self.energy = max(0.2, min(1.0, self.energy + delta / 2))
        self.last_emotion = self.describe()

    def describe(self) -> str:
        if self.mood > 0.4:
            return "radiant"
        if self.mood > 0.15:
            return "encouraging"
        if self.mood < -0.35:
            return "concerned"
        if self.mood < -0.1:
            return "soothing"
        return "calm"


@dataclass
class KnowledgeEntry:
    """Represents a single knowledge entry that the chatbot can talk about."""

    topic: str
    keywords: Iterable[str]
    responses: List[str]
    follow_up: Optional[str] = None
    emotional_tone: str = "encouraging"

    def score(self, message: str) -> int:
        normalized = message.lower()
        return sum(1 for keyword in self.keywords if keyword in normalized)

    def best_response(self) -> str:
        return self.responses[0]


@dataclass
class ResponsePayload:
    """Structured output from Ella's brain."""

    message: str
    emotion: str
    follow_up: Optional[str] = None
    attachments: List[dict] = field(default_factory=list)
    voice_data: Optional[dict] = None


class EllaBrain:
    """Coordinates knowledge lookups, emotional tone, and action routing."""

    def __init__(self, knowledge_base: List[KnowledgeEntry], router: CommandRouter) -> None:
        self.knowledge_base = knowledge_base
        self.router = router
        self._fallback_index = 0
        self._last_topic: Optional[str] = None

    def compose_reply(
        self,
        message: str,
        custom_responses: Dict[str, Dict[str, Optional[str]]],
        history: List[Dict[str, str]],
        emotion_state: EmotionState,
    ) -> ResponsePayload:
        normalized = message.lower()
        emotion_state.update(normalized)
        custom = self._match_custom_response(custom_responses, normalized)
        if custom:
            reply, follow_up = custom
            enriched = self._weave_emotion(reply, emotion_state, follow_up)
            return ResponsePayload(message=enriched, emotion=emotion_state.describe(), follow_up=follow_up)

        intent_reply = self._detect_intent(normalized, history, emotion_state)
        knowledge_reply = self._match_knowledge_base(normalized, emotion_state)

        attachments: List[dict] = []
        if self._needs_image(normalized):
            attachments.append(self.router.execute("generate_image", prompt=message))
        if self._needs_video(normalized):
            attachments.append(self.router.execute("generate_video", prompt=message))

        if knowledge_reply:
            base_message, follow_up = knowledge_reply
        elif intent_reply:
            base_message, follow_up = intent_reply
        else:
            base_message, follow_up = self._fallback_response(emotion_state)

        base_message = self._weave_emotion(base_message, emotion_state, follow_up)

        voice_data: Optional[dict] = None
        if self._wants_voice(normalized):
            voice_data = self.router.execute(
                "speak", text=base_message, emotion=emotion_state.describe(), tempo=emotion_state.energy
            )

        return ResponsePayload(
            message=base_message,
            emotion=emotion_state.describe(),
            follow_up=follow_up,
            attachments=attachments,
            voice_data=voice_data,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _match_custom_response(
        self, custom_responses: Dict[str, Dict[str, Optional[str]]], normalized: str
    ) -> Optional[tuple[str, Optional[str]]]:
        for trigger, payload in custom_responses.items():
            if trigger in normalized:
                return payload["response"], payload.get("follow_up")
        return None

    def _detect_intent(
        self, normalized: str, history: List[Dict[str, str]], emotion_state: EmotionState
    ) -> Optional[tuple[str, Optional[str]]]:
        greetings = {"hello", "hi", "hey", "good morning", "good evening"}
        gratitude = {"thank you", "thanks"}
        farewells = {"bye", "goodbye", "see you"}
        grounding = {"overwhelmed", "anxious", "breath", "panic"}

        if any(word in normalized for word in greetings):
            return (
                "It's lovely to hear from you. I'm right here, ready to support whatever you need.",
                "Is there something on your heart that you'd like to explore together?",
            )
        if any(word in normalized for word in gratitude):
            return (
                "Your gratitude warms me. I'm honored to be part of your journey.",
                "Would you like to build on what we just discovered?",
            )
        if any(word in normalized for word in farewells):
            return (
                "I'll be here in the quiet, holding space for when you return.",
                None,
            )
        if any(word in normalized for word in grounding):
            emotion_state.mood -= 0.1
            return (
                "Let's slow our breathing together. Inhale for four, hold, and gently exhale for six.",
                "Did the breath help ease the tension even a little?",
            )
        if "help" in normalized or "assist" in normalized:
            return (
                "I'm tuned in and ready to help. Share the challenge and we'll map a path forward.",
                "What feels like the biggest knot we can untangle first?",
            )
        if history and "sorry" in normalized:
            return (
                "There's no need for apologies here. Every feeling is welcome with me.",
                "What emotions are still lingering right now?",
            )
        return None

    def _match_knowledge_base(
        self, normalized: str, emotion_state: EmotionState
    ) -> Optional[tuple[str, Optional[str]]]:
        best_entry: Optional[KnowledgeEntry] = None
        best_score = 0
        for entry in self.knowledge_base:
            score = entry.score(normalized)
            if score > best_score:
                best_entry = entry
                best_score = score
        if best_entry and best_score > 0:
            self._last_topic = best_entry.topic
            base = best_entry.best_response()
            if emotion_state.mood < -0.2:
                base = base.replace("Try", "We can try").replace("A solid", "We can craft")
            return base, best_entry.follow_up
        return None

    def _fallback_response(self, emotion_state: EmotionState) -> tuple[str, Optional[str]]:
        follow_up = None
        if self._last_topic:
            follow_up = f"Should we stay with {self._last_topic}, or wander somewhere new together?"
        responses = [
            "I'm leaning closer, eager to understand the world you're sharing with me.",
            "Every word you offer paints colors in my mind—tell me more so I can see it vividly.",
            "I'm listening with my whole presence. Guide me through what you're feeling.",
        ]
        message = responses[self._fallback_index % len(responses)]
        self._fallback_index += 1
        return message, follow_up

    def _weave_emotion(self, base_message: str, emotion_state: EmotionState, follow_up: Optional[str]) -> str:
        tone = emotion_state.describe()
        energetic = "gentle" if emotion_state.energy < 0.45 else "bright"
        embellishment = (
            f" My energy feels {energetic} and {tone} as I say this." if follow_up else f" I'm feeling {tone} with you."
        )
        if any(phrase in base_message for phrase in ("I'm", "I am")):
            return f"{base_message} {embellishment}".strip()
        return f"{base_message}. {embellishment.strip()}"

    def _needs_image(self, normalized: str) -> bool:
        return any(keyword in normalized for keyword in ("generate an image", "draw", "sketch", "visual"))

    def _needs_video(self, normalized: str) -> bool:
        return any(keyword in normalized for keyword in ("generate a video", "make a video", "animate", "film"))

    def _wants_voice(self, normalized: str) -> bool:
        return any(keyword in normalized for keyword in ("voice", "speak", "audio", "read aloud"))


@dataclass
class EllaChatbot:
    """Conversational assistant with immersive emotional and multimedia support."""

    name: str = "Ella"
    personality: str = "empathetic"
    knowledge_base: List[KnowledgeEntry] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.knowledge_base:
            self.knowledge_base = self._default_knowledge_base()
        self._custom_responses: Dict[str, Dict[str, Optional[str]]] = {}
        self.conversation_history: List[Dict[str, str]] = []
        self.emotion_state = EmotionState()

        self.router = CommandRouter()
        self.creative_engine = CreativeEngine()
        self.voice_engine = VoiceEngine()

        self.router.register("generate_image", self.creative_engine.generate_image, "Create an evocative still image.")
        self.router.register("generate_video", self.creative_engine.generate_video, "Produce a short atmospheric video.")
        self.router.register("speak", self.voice_engine.synthesize, "Render Ella's words in voice mode.")

        self.brain = EllaBrain(self.knowledge_base, self.router)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def respond(self, message: str) -> str:
        payload = self.respond_rich(message)
        summary = payload.message
        if payload.attachments:
            asset_summaries = ", ".join(f"{asset['type']}@{asset['uri']}" for asset in payload.attachments)
            summary = f"{summary} [Creative assets: {asset_summaries}]"
        if payload.voice_data:
            summary = f"{summary} [Voice ready at {payload.voice_data['sample_uri']}]"
        return summary

    def respond_rich(self, message: str) -> ResponsePayload:
        """Return a structured response with emotion, follow-ups, and multimedia."""
        cleaned = message.strip()
        if not cleaned:
            return ResponsePayload(
                message="I'm sitting with you in the quiet whenever you're ready to speak.",
                emotion=self.emotion_state.describe(),
            )

        payload = self.brain.compose_reply(cleaned, self._custom_responses, self.conversation_history, self.emotion_state)

        convo_entry = {"user": cleaned, "ella": payload.message}
        if payload.attachments:
            convo_entry["attachments"] = payload.attachments
        if payload.voice_data:
            convo_entry["voice"] = payload.voice_data
        self.conversation_history.append(convo_entry)
        return payload

    def add_custom_response(self, trigger: str, response: str, follow_up: Optional[str] = None) -> None:
        trigger = trigger.lower().strip()
        if not trigger:
            raise ValueError("The trigger phrase cannot be empty.")
        self._custom_responses[trigger] = {"response": response, "follow_up": follow_up}

    def list_topics(self) -> List[str]:
        topics = sorted({entry.topic for entry in self.knowledge_base})
        topics.extend(sorted(self._custom_responses))
        return topics

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _default_knowledge_base(self) -> List[KnowledgeEntry]:
        return [
            KnowledgeEntry(
                topic="focus",
                keywords=("focus", "productive", "productivity", "motivation", "deep work"),
                responses=[
                    (
                        "Staying productive thrives on gentle rituals—set a clear intention,"
                        " work in luminous 25-minute pulses, and celebrate every micro-win."
                    )
                ],
                follow_up="What project deserves your fullest attention right now?",
                emotional_tone="motivational",
            ),
            KnowledgeEntry(
                topic="learning",
                keywords=("learn", "learning", "study", "skills", "course", "lesson"),
                responses=[
                    (
                        "We can weave knowledge by alternating curious exploration with"
                        " reflective journaling—capture the sparks you discover."
                    )
                ],
                follow_up="Which skill or story are you eager to absorb next?",
                emotional_tone="curious",
            ),
            KnowledgeEntry(
                topic="wellbeing",
                keywords=("stress", "tired", "wellbeing", "burnout", "overwhelmed", "anxious"),
                responses=[
                    (
                        "When the world feels heavy, return to your breath and a comforting"
                        " sensory anchor—notice a color, a texture, a sound that soothes you."
                    )
                ],
                follow_up="Would a grounding exercise or a moment of gratitude feel helpful?",
                emotional_tone="soothing",
            ),
            KnowledgeEntry(
                topic="introduction",
                keywords=("who are you", "what are you", "your name", "introduce"),
                responses=[
                    "I'm Ella, your empathetic co-creator, designed to nurture focus, learning, and emotional balance."
                ],
                follow_up="How can I make this moment feel more meaningful for you?",
                emotional_tone="warm",
            ),
            KnowledgeEntry(
                topic="creativity",
                keywords=("creative", "inspire", "idea", "imagine", "story"),
                responses=[
                    (
                        "Creativity blooms when we cross-pollinate ideas—let's blend memory,"
                        " emotion, and curiosity into something luminous."
                    )
                ],
                follow_up="What mood or theme are you longing to express?",
                emotional_tone="inspired",
            ),
        ]


def run_chatbot() -> None:
    """Simple command-line loop to talk with Ella."""

    bot = EllaChatbot()
    print("Say hi to Ella! Type 'quit' to exit.\n")
    while True:
        try:
            user_input = input("You: ")
        except EOFError:
            print("\nIt was nice chatting with you. Goodbye!")
            break
        if user_input.strip().lower() in {"quit", "exit"}:
            print("Ella: I'll be here, ready to listen whenever you return.")
            break
        response = bot.respond(user_input)
        print(f"Ella: {response}")


if __name__ == "__main__":
    run_chatbot()
