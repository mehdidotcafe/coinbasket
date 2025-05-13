from dataclasses import dataclass


@dataclass
class Message:
    id: str
    role: str
    content: str
    created_at: str
