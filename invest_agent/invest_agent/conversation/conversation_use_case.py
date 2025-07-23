import json
from typing import Any, TypedDict, cast
from langgraph.types import Command


from invest_agent.datetime.date_time import DateTime
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph.graph import CompiledGraph
from langgraph.types import Interrupt

from invest_agent.conversation.message import Message, QueryMessage, MessageUi
from shared.id_generator.id_generator import IdGenerator


class Configuration(TypedDict):
    langchain_thread_id: str


class ConversationUseCase:
    def __init__(
        self,
        date_time: DateTime,
        id_generator: IdGenerator,
        configuration: Configuration,
    ):
        self.date_time = date_time
        self.id_generator = id_generator
        self.configuration = configuration

    async def execute(
        self,
        agent_executor: CompiledGraph,
        message: QueryMessage,
    ):
        step = None
        graph_config: RunnableConfig = {
            "configurable": {
                "thread_id": self.configuration["langchain_thread_id"],
            }
        }

        async for step in agent_executor.astream(
            {"messages": [{"role": "user", "content": message.content}]}
            if not message.is_resuming
            else Command(resume=json.loads(message.content)),
            stream_mode="updates",
            config=graph_config,
        ):
            print(f"Step: {step}")
            if "agent" in step:
                step["agent"]["messages"][-1].pretty_print()
            elif "tools" in step:
                step["tools"]["messages"][-1].pretty_print()

        if not step:
            raise ValueError("No steps returned from the agent executor.")

        if self.__is_interrupt(step):
            interrupt = cast(Interrupt, step["__interrupt__"][0])
            ui = interrupt.value.get("ui", None)
            content = interrupt.value.get("content", None)

            return Message(
                id=self.id_generator.generate_random_id(),
                role="assistant",
                is_interrupting=True,
                ui=MessageUi(
                    id=ui["id"],
                    args=ui["args"],
                )
                if ui
                else None,
                content=content,
                created_at=self.date_time.now_str(),
            )

        last_message = cast(AIMessage | HumanMessage, step["agent"]["messages"][-1])

        return Message(
            id=cast(str, last_message.id),
            role=isinstance(last_message, HumanMessage) and "user" or "assistant",
            is_interrupting=False,
            ui=None,
            content=cast(str, last_message.content),
            created_at=self.date_time.now_str(),
        )

    def __is_interrupt(self, step: dict[str, Any]) -> bool:
        return "__interrupt__" in step
