from abc import ABC, abstractmethod
from typing import Any

from api.conversation.message import Message
from langgraph.graph.state import CompiledStateGraph


class ConversationRepository(ABC):
    @abstractmethod
    async def start(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_messages(self, thread_id: str) -> list[Message]:
        raise NotImplementedError

    @abstractmethod
    async def get_interrupts(
        self, thread_id: str, agent_executor: CompiledStateGraph[Any]
    ) -> list[Message]:
        raise NotImplementedError
