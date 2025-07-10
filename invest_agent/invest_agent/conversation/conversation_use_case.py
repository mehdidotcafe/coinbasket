from typing import Any, TypedDict, cast

import aiosqlite

from invest_agent.datetime.date_time import DateTime
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from invest_agent.conversation.message import Message


Tool = Any


class Configuration(TypedDict):
    langchain_thread_id: str
    agent_name: str
    chat_model: str
    chat_provider: str
    chat_provider_api_key: str


class ConversationUseCase:
    def __init__(self, date_time: DateTime, configuration: Configuration):
        self.configuration = configuration
        self.date_time = date_time

        self.llm = init_chat_model(
            model=configuration["chat_model"],
            model_provider=configuration["chat_provider"],
            api_key=configuration["chat_provider_api_key"],
        )

    async def execute(
        self,
        tools: list[Tool],
        message: Message,
    ):
        async with aiosqlite.connect("./database/langchain_graphs.db") as conn:
            agent_executor = self.__create_agent_executor(conn, tools)

            graph_config: RunnableConfig = {
                "configurable": {
                    "thread_id": self.configuration["langchain_thread_id"],
                }
            }

            async for step in agent_executor.astream(
                {"messages": [{"role": "user", "content": message.content}]},
                stream_mode="values",
                config=graph_config,
            ):
                step["messages"][-1].pretty_print()

            last_message = step["messages"][-1]

            return Message(
                id=cast(str, last_message.id),
                role=isinstance(last_message, HumanMessage) and "user" or "assistant",
                content=cast(str, last_message.content),
                created_at=self.date_time.now_str(),
            )

    def __create_agent_executor(self, conn: aiosqlite.Connection, tools: list[Tool]):
        sqlite_memory = AsyncSqliteSaver(conn)

        agent_executor = create_react_agent(
            self.llm,
            tools,
            checkpointer=sqlite_memory,
            prompt=SystemMessage(
                f"Your name is {self.configuration['agent_name']}.  "
                f"Today is {self.date_time.now_str()}.  "
                "Your goal is to manage a portfolio made of assets. An asset is either a token or a basket of tokens.  "
                "Users can buy, sell, or swap assets in their portfolio.  "
                "Before buying, selling or swapping assets, always show the user the investment plan you are creating by showing the list of assets to buy, sell or swap.  "
                "When you display a token, always display its display name, ticker and address by using this link 'https://bscscan.com/token/[token_address]'. Don't mention excluded assets.  "
                "After each answer, ask the user if he wants to add or remove any asset from the portfolio or if he wants to proceed.  "
                "Always ask for the user's confirmation before updating the portfolio and show a message mentioning that he should do his own research (DYOR) before investing.  "
                "If you don't know the answer, just say that you don't know and mention what you can do, don't try to make up an answer.  "
            ),
        )

        return agent_executor
