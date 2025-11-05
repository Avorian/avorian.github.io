"""Core implementation of the Ella Prototype chatbot."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional


@dataclass
class KnowledgeEntry:
    """Represents a single knowledge entry that the chatbot can talk about."""

    topic: str
    keywords: Iterable[str]
    responses: List[str]
    follow_up: Optional[str] = None

    def score(self, message: str) -> int:
        """Return a simple relevancy score based on keyword matches."""
        normalized = message.lower()
        score = sum(1 for keyword in self.keywords if keyword in normalized)
        return score

    def best_response(self) -> str:
        """Return the most appropriate response for the entry."""
        return self.responses[0]


@dataclass
class EllaChatbot:
    """Conversational assistant with a lightweight rule-based engine.

    The prototype keeps a history of the conversation, matches user prompts
    against a small knowledge base, and supports custom responses that can be
    taught while running.
    """

    name: str = "Ella"
    personality: str = "friendly"
    knowledge_base: List[KnowledgeEntry] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.knowledge_base:
            self.knowledge_base = self._default_knowledge_base()
        self._custom_responses: Dict[str, Dict[str, Optional[str]]] = {}
        self.conversation_history: List[Dict[str, str]] = []
        self._last_topic: Optional[str] = None
        self._fallback_index = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def respond(self, message: str) -> str:
        """Return Ella's response to ``message``."""
        message = message.strip()
        if not message:
            return "I'm here whenever you're ready to chat."

        normalized = message.lower()

        custom_match = self._match_custom_response(normalized)
        if custom_match is not None:
            response = custom_match
        else:
            knowledge_response = self._match_knowledge_base(normalized)
            intent_response = self._detect_intent(normalized)
            if knowledge_response:
                response = knowledge_response
            elif intent_response:
                response = intent_response
            else:
                response = self._fallback_response(normalized)

        self.conversation_history.append({"user": message, "ella": response})
        return response

    def add_custom_response(self, trigger: str, response: str, follow_up: Optional[str] = None) -> None:
        """Teach the chatbot a new response.

        Parameters
        ----------
        trigger:
            Substring that should trigger the response when included in a
            message. The matching is case-insensitive.
        response:
            The reply Ella should give when the trigger is found.
        follow_up:
            Optional follow-up question to keep the conversation flowing.
        """

        trigger = trigger.lower().strip()
        if not trigger:
            raise ValueError("The trigger phrase cannot be empty.")
        self._custom_responses[trigger] = {"response": response, "follow_up": follow_up}

    def list_topics(self) -> List[str]:
        """Return a sorted list of topics the chatbot can discuss."""
        topics = sorted({entry.topic for entry in self.knowledge_base})
        topics.extend(sorted(self._custom_responses))
        return topics

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _match_custom_response(self, normalized: str) -> Optional[str]:
        for trigger, payload in self._custom_responses.items():
            if trigger in normalized:
                response = payload["response"]
                follow_up = payload.get("follow_up")
                if follow_up:
                    return f"{response} {follow_up}"
                return response
        return None

    def _detect_intent(self, normalized: str) -> Optional[str]:
        greetings = {"hello", "hi", "hey", "good morning", "good evening"}
        gratitude = {"thank you", "thanks"}
        farewells = {"bye", "goodbye", "see you"}
        asking_help = {"help", "assist", "support"}

        if any(word in normalized for word in greetings):
            return "Hello! I'm Ella, your friendly assistant. How can I help you today?"
        if any(word in normalized for word in gratitude):
            return "You're welcome! Let me know if there's anything else you need."
        if any(word in normalized for word in farewells):
            return "Goodbye for now. I'm always here if you want to chat again."
        if any(word in normalized for word in asking_help):
            return (
                "I'm here to support you with learning, productivity, and wellbeing. "
                "Tell me more about what you need help with."
            )
        return None

    def _match_knowledge_base(self, normalized: str) -> Optional[str]:
        best_entry: Optional[KnowledgeEntry] = None
        best_score = 0
        for entry in self.knowledge_base:
            score = entry.score(normalized)
            if score > best_score:
                best_entry = entry
                best_score = score
        if best_entry and best_score > 0:
            self._last_topic = best_entry.topic
            response = best_entry.best_response()
            if best_entry.follow_up:
                response = f"{response} {best_entry.follow_up}"
            return response
        return None

    def _fallback_response(self, normalized: str) -> str:
        follow_up = None
        if self._last_topic:
            follow_up = (
                "We can keep exploring "
                f"{self._last_topic} if you'd like, or we can switch topics."
            )
        responses = [
            "I'm still learning, but I'd love to hear more so I can understand better.",
            "That's interesting! Could you tell me a bit more?",
            "I might not have a perfect answer yet, but I'm here to listen.",
        ]
        response = responses[self._fallback_index % len(responses)]
        self._fallback_index += 1
        if follow_up:
            return f"{response} {follow_up}"
        return response

    def _default_knowledge_base(self) -> List[KnowledgeEntry]:
        return [
            KnowledgeEntry(
                topic="focus",
                keywords=("focus", "productive", "productivity", "motivation"),
                responses=[
                    (
                        "Staying productive can start with tiny habits. Try working in"
                        " short, focused intervals and reward yourself with breaks."
                    )
                ],
                follow_up="What kind of work are you hoping to stay on top of?",
            ),
            KnowledgeEntry(
                topic="learning",
                keywords=("learn", "learning", "study", "skills", "course"),
                responses=[
                    (
                        "A solid learning plan mixes practice with reflection."
                        " Writing down what you understood after each session helps."
                    )
                ],
                follow_up="Which skill are you most excited to improve?",
            ),
            KnowledgeEntry(
                topic="wellbeing",
                keywords=("stress", "tired", "wellbeing", "burnout", "overwhelmed"),
                responses=[
                    (
                        "When stress builds up, it helps to pause for a few slow breaths"
                        " and check in with how your body feels to protect your wellbeing."
                    )
                ],
                follow_up="Would you like a short breathing exercise or another tip?",
            ),
            KnowledgeEntry(
                topic="introduction",
                keywords=("who are you", "what are you", "your name"),
                responses=[
                    "I'm Ella, a prototype companion built to encourage learning and wellbeing."
                ],
                follow_up="What would you like to explore together?",
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
            print("Ella: Goodbye for now. I'm always here if you want to chat again.")
            break
        response = bot.respond(user_input)
        print(f"Ella: {response}")


if __name__ == "__main__":
    run_chatbot()
