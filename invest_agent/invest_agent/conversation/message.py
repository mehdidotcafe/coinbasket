from dataclasses import dataclass
from typing import Literal


@dataclass
class Message:
    id: str
    role: Literal["user", "assistant", "tool"]
    content: str
    created_at: str
