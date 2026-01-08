from typing import TypedDict, cast, Any

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from api.conversation.message import Message
from api.conversation.repository.conversation_repository import (
    ConversationRepository,
)
from langgraph.graph.state import CompiledStateGraph

from api.datetime.date_time import DateTime
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, AIMessage
from api.conversation.interrupt import Interrupt
from api.shared.id_generator.id_generator import IdGenerator


class Configuration(TypedDict):
    database_user: str
    database_password: str
    database_host: str
    database_name: str
    database_port: int


class LangchainPostgresqlConversationRepository(ConversationRepository):
    """
    LangchainPostgresqlConversationRepository is a class that implements the ConversationRepository interface
    using PostgreSQL as the backend database. It provides methods to save and retrieve conversations
    from the PostgreSQL database.
    """

    def __init__(
        self,
        date_time: DateTime,
        id_generator: IdGenerator,
        configuration: Configuration,
    ):
        self.date_time = date_time
        self.id_generator = id_generator
        self.configuration = configuration

    async def start(self):
        async with AsyncPostgresSaver.from_conn_string(
            f"postgres://{self.configuration['database_user']}:{self.configuration['database_password']}@{self.configuration['database_host']}:{self.configuration['database_port']}/{self.configuration['database_name']}"
        ) as checkpointer:
            await checkpointer.setup()

    async def get_messages(self, thread_id: str) -> list[Message]:
        async with AsyncPostgresSaver.from_conn_string(
            f"postgres://{self.configuration['database_user']}:{self.configuration['database_password']}@{self.configuration['database_host']}:{self.configuration['database_port']}/{self.configuration['database_name']}"
        ) as checkpointer:
            graph_config: RunnableConfig = {
                "configurable": {
                    "thread_id": thread_id,
                }
            }

            checkpoint_data = await checkpointer.aget(graph_config)

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
