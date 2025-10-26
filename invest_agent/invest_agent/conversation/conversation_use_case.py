import json
from typing import Any, TypedDict, cast
from langgraph.types import Command


from invest_agent.datetime.date_time import DateTime
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Interrupt as LanggraphInterrupt

from invest_agent.conversation.message import Message, QueryMessage
from shared.id_generator.id_generator import IdGenerator
from invest_agent.conversation.interrupt import Interrupt


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
        agent_executor: CompiledStateGraph[Any],
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

            if Interrupt.is_step_interrupt(step):
                return Interrupt.to_message(
                    cast(LanggraphInterrupt, step["__interrupt__"][0]),
                    self.id_generator.generate_random_id(),
                    self.date_time.now_str(),
                )

        if not step:
            raise ValueError("No steps returned from the agent executor.")

        last_message = cast(AIMessage | HumanMessage, step["agent"]["messages"][-1])

        return Message(
            id=cast(str, last_message.id),
            role=isinstance(last_message, HumanMessage) and "user" or "assistant",
            is_interrupting=False,
            ui=None,
            content=cast(str, last_message.content),
            created_at=self.date_time.now_str(),
        )
