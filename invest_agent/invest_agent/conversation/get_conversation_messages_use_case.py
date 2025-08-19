from invest_agent.conversation.repository.conversation_repository import (
    ConversationRepository,
)
from invest_agent.conversation.message import Message

from langgraph.graph.state import CompiledStateGraph
from typing import Any, TypedDict


class Configuration(TypedDict):
    langchain_thread_id: str


class GetConversationMessagesUseCase:
    def __init__(
        self,
        conversation_repository: ConversationRepository,
    ):
        self.conversation_repository = conversation_repository

    async def execute(
        self, thread_id: str, agent_executor: CompiledStateGraph[Any]
    ) -> list[Message]:
        messages = await self.conversation_repository.get_messages(thread_id)

        interrupt_messages = await self.conversation_repository.get_interrupts(
            thread_id, agent_executor
        )

        return messages + interrupt_messages
