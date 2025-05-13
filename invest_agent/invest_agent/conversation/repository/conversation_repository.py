from abc import ABC, abstractmethod

from invest_agent.conversation.message import Message


class ConversationRepository(ABC):
    @abstractmethod
    async def get_messages(self, thread_id: str) -> list[Message]:
        raise NotImplementedError
