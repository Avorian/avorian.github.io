import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

import httpx


class LLMClient:
    """Simple client for interacting with a local LLM gateway."""

    def __init__(self, base_url: str, mode: str = "local", timeout: int = 20, model: Optional[str] = None):
        self.base_url = base_url
        self.mode = mode
        self.timeout = timeout
        self.model = model or "local-model"
        self._client = httpx.AsyncClient(timeout=self.timeout)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def chat(self, system_prompt: str, messages: List[Dict[str, str]]) -> str:
        if self.mode not in {"local", "hybrid", "cloud"}:
            logging.warning("Unknown llm mode '%s'; defaulting to local.", self.mode)

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "system", "content": system_prompt}] + messages,
        }

        try:
            response = await self._client.post(self.base_url, json=payload)
            response.raise_for_status()
            data = response.json()
            # Support OpenAI-style responses
            choices = data.get("choices") or []
            if choices:
                return choices[0].get("message", {}).get("content", "")
            # If the gateway returns raw text
            if isinstance(data, dict) and "content" in data:
                return str(data["content"])
        except (httpx.HTTPError, json.JSONDecodeError) as exc:
            logging.error("LLM request failed: %s", exc)

        return "I ran into a hiccup reaching the local model. I'll keep things simple for now."


__all__ = ["LLMClient"]
