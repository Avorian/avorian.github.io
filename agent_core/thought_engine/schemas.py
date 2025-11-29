from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ChatReply(BaseModel):
    text: str = Field(..., description="User-facing response text from Oracle")


class ToolAction(BaseModel):
    tool_name: str = Field(..., description="Name of the tool to invoke")
    args: Dict[str, Any] = Field(default_factory=dict, description="Arguments for the tool")


class DecisionResponse(BaseModel):
    reply: ChatReply
    actions: List[ToolAction] = Field(default_factory=list)


class OracleContext(BaseModel):
    user: str
    channel: Optional[str]
    game: Optional[str] = None
    message_id: Optional[int] = None


__all__ = [
    "ChatReply",
    "DecisionResponse",
    "OracleContext",
    "ToolAction",
]
