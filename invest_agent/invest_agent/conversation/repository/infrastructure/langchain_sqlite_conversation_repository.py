from typing import cast
import aiosqlite
from invest_agent.conversation.message import Message
from invest_agent.conversation.repository.conversation_repository import (
    ConversationRepository,
)

from invest_agent.datetime.date_time import DateTime
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langchain_core.messages import HumanMessage, AIMessage


class LangchainSqliteConversationRepository(ConversationRepository):
    """
    LangchainSqliteRepository is a class that implements the ConversationRepository interface
    using SQLite as the backend database. It provides methods to save and retrieve conversations
    from the SQLite database.
    """

    def __init__(self, db_path: str, date_time: DateTime):
        self.db_path = db_path
        self.date_time = date_time

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
            role=isinstance(langchain_message, HumanMessage) and "user" or "assistant",
            content=cast(str, langchain_message.content),
            created_at=self.date_time.now_str(),
        )
