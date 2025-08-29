from typing import Any
from langgraph.types import Interrupt as LanggraphInterrupt

from invest_agent.conversation.message import Message, MessageUi


class Interrupt:
    @staticmethod
    def is_step_interrupt(maybeInterrupt: dict[str, Any]) -> bool:
        return "__interrupt__" in maybeInterrupt

    @staticmethod
    def to_message(interrupt: LanggraphInterrupt, id: str, created_at: str) -> Message:
        ui = interrupt.value.get("ui", None)
        content = interrupt.value.get("content", None)

        return Message(
            id=id,
            role="assistant",
            is_interrupting=True,
            ui=MessageUi(
                id=ui["id"],
                args=ui["args"],
            )
            if ui
            else None,
            content=content,
            created_at=created_at,
        )
