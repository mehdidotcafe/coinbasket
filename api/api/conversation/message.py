from dataclasses import dataclass
from typing import Any, Literal


@dataclass
class MessageUi:
    id: str
    args: dict[str, Any]


@dataclass
class Message:
    id: str
    role: Literal["user", "assistant"]
    is_interrupting: bool
    ui: MessageUi | None
    content: str | None
    created_at: str


@dataclass
class QueryMessage:
    id: str
    role: Literal["user"]
    is_resuming: bool
    content: str
    created_at: str
