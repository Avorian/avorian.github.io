import json
import logging
from typing import Dict, List

from .llm_client import LLMClient
from .schemas import ChatReply, DecisionResponse, OracleContext, ToolAction


SYSTEM_PROMPT = (
    "You are Oracle, a warm, witty, and practical in-game assistant for PC gamers. "
    "You chat through Discord overlay while the player is in-game. "
    "Provide concise advice, call out key tips, and suggest clips when great moments happen. "
    "Respond with a short reply and optional tool actions in JSON."
)


class ThoughtRouter:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    async def decide_response(self, message: str, context: OracleContext) -> DecisionResponse:
        prompt_messages: List[Dict[str, str]] = [
            {"role": "user", "content": self._build_user_prompt(message, context)},
        ]

        raw_output = await self.llm_client.chat(SYSTEM_PROMPT, prompt_messages)
        parsed = self._parse_output(raw_output)
        return parsed

    def _build_user_prompt(self, message: str, context: OracleContext) -> str:
        lines = [f"User: {context.user}"]
        if context.game:
            lines.append(f"Game: {context.game}")
        if context.channel:
            lines.append(f"Channel: {context.channel}")
        lines.append(f"Message: {message}")
        lines.append(
            "Reply with JSON: {\"reply\":{\"text\":str}, \"actions\":[{\"tool_name\":str, \"args\":{}}]}"
        )
        return "\n".join(lines)

    def _parse_output(self, text: str) -> DecisionResponse:
        try:
            payload = json.loads(text)
            reply = ChatReply(text=str(payload.get("reply", {}).get("text", "")))
            actions_payload = payload.get("actions") or []
            actions = []
            for item in actions_payload:
                try:
                    actions.append(ToolAction(**item))
                except Exception as exc:  # pydantic error fallback
                    logging.warning("Skipping invalid tool action %s: %s", item, exc)
            if not reply.text:
                reply = ChatReply(text=text)
            return DecisionResponse(reply=reply, actions=actions)
        except json.JSONDecodeError:
            logging.warning("LLM reply was not valid JSON; falling back to raw text.")
            safe_reply = ChatReply(text=text.strip() or "I'll keep an eye on things.")
            return DecisionResponse(reply=safe_reply, actions=[])


__all__ = ["ThoughtRouter"]
