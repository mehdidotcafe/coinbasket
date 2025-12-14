from typing import cast, Any
import aiosqlite
from api.conversation.message import Message
from api.conversation.repository.conversation_repository import (
    ConversationRepository,
)
from langgraph.graph.state import CompiledStateGraph

from api.datetime.date_time import DateTime
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langchain_core.messages import HumanMessage, AIMessage
from api.conversation.interrupt import Interrupt
from shared.id_generator.id_generator import IdGenerator


class LangchainSqliteConversationRepository(ConversationRepository):
    """
    LangchainSqliteRepository is a class that implements the ConversationRepository interface
    using SQLite as the backend database. It provides methods to save and retrieve conversations
    from the SQLite database.
    """

    def __init__(self, db_path: str, date_time: DateTime, id_generator: IdGenerator):
        self.db_path = db_path
        self.date_time = date_time
        self.id_generator = id_generator

    async def get_messages(self, thread_id: str) -> list[Message]:
        async with aiosqlite.connect(self.db_path, check_same_thread=False) as db:
            graph_config: RunnableConfig = {
                "configurable": {
                    "thread_id": thread_id,
                }
            }
            store = AsyncSqliteSaver(db)

            checkpoint_data = await store.aget(graph_config)

            if not checkpoint_data:
                return []

            messages = checkpoint_data["channel_values"]["messages"]

            return [
                self.__map_langchain_message_to_message(m)
                for m in messages
                if (isinstance(m, HumanMessage) or isinstance(m, AIMessage))
                and m.content not in ["", " "]
            ]

    async def get_interrupts(
        self, thread_id: str, agent_executor: CompiledStateGraph[Any]
    ) -> list[Message]:
        graph_config: RunnableConfig = {
            "configurable": {
                "thread_id": thread_id,
            }
        }
        snap = await agent_executor.aget_state(graph_config)

        return [
            Interrupt.to_message(
                interrupt,
                self.id_generator.generate_random_id(),
                self.date_time.now_str(),
            )
            for interrupt in snap.interrupts
        ]

    def __map_langchain_message_to_message(
        self, langchain_message: HumanMessage | AIMessage
    ) -> Message:
        """
        Map a Langchain message to the Message class.

        Args:
            langchain_message: The Langchain message to map.

        Returns:
            Message: The mapped Message object.
        """
        return Message(
            id=cast(str, langchain_message.id),
            is_interrupting=False,
            ui=None,
            role=isinstance(langchain_message, HumanMessage) and "user" or "assistant",
            content=langchain_message.content
            if isinstance(langchain_message.content, str)
            else self._map_langchain_ai_message_content_to_content(
                langchain_message.content
            ),
            created_at=self.date_time.now_str(),
        )

    def _map_langchain_ai_message_content_to_content(
        self, content: list[dict[Any, Any]]
    ) -> str:
        return cast(
            str,
            next((c["text"] for c in content if c["type"] == "text"), ""),
        )
