import json
from typing import Any, cast
from api.conversation.exception.waiting_interrupt import WaitingInterrupt
from langgraph.types import Command


from api.datetime.date_time import DateTime
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Interrupt as LanggraphInterrupt

from api.conversation.message import Message, MessageUi, QueryMessage
from api.conversation.interrupt import Interrupt


class ConversationUseCase:
    def __init__(
        self,
        date_time: DateTime,
    ):
        self.date_time = date_time

    async def execute(
        self,
        agent_executor: CompiledStateGraph[Any],
        thread_id: str,
        message: QueryMessage,
    ) -> list[Message]:
        step = None
        graph_config: RunnableConfig = {
            "configurable": {
                "thread_id": thread_id,
            }
        }

        snap = await agent_executor.aget_state(graph_config)

        if snap.interrupts and not message.is_resuming:
            raise WaitingInterrupt()

        messages: list[Message] = []

        async for step in agent_executor.astream(
            {"messages": [{"role": "user", "content": message.content}]}
            if not message.is_resuming
            else Command(resume=json.loads(message.content)),
            stream_mode="updates",
            config=graph_config,
        ):
            print(f"Step: {step}")
            if "model" in step:
                step["model"]["messages"][-1].pretty_print()
            elif "tools" in step:
                step["tools"]["messages"][-1].pretty_print()
                if "ui" in step["tools"]:
                    messages.append(
                        Message(
                            id=step["tools"]["ui"]["id"],
                            role="assistant",
                            is_interrupting=False,
                            ui=MessageUi(
                                id=cast(str, step["tools"]["ui"]["name"]),
                                args=cast(dict[str, Any], step["tools"]["ui"]["props"]),
                            ),
                            content=None,
                            created_at=self.date_time.now_str(),
                        )
                    )

            if Interrupt.is_step_interrupt(step):
                langgraph_interrupt = cast(LanggraphInterrupt, step["__interrupt__"][0])

                return [
                    *messages,
                    Interrupt.to_message(
                        langgraph_interrupt,
                        langgraph_interrupt.id,
                        self.date_time.now_str(),
                    ),
                ]

        if not step:
            raise ValueError("No steps returned from the agent executor.")

        last_message = cast(AIMessage | HumanMessage, step["model"]["messages"][-1])
        last_message_text = cast(
            str,
            next((c["text"] for c in last_message.content if c["type"] == "text"), ""),
        )

        return [
            *messages,
            Message(
                id=cast(str, last_message.id),
                role=isinstance(last_message, HumanMessage) and "user" or "assistant",
                is_interrupting=False,
                ui=None,
                content=last_message_text,
                created_at=self.date_time.now_str(),
            ),
        ]
