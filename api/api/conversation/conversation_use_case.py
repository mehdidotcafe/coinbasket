import json
from collections.abc import AsyncGenerator
from typing import Any, cast

from langgraph.types import Command

from api.conversation.exception.waiting_interrupt import WaitingInterrupt
from api.datetime.date_time import DateTime
from api.shared.id_generator.id_generator import IdGenerator
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Interrupt as LanggraphInterrupt

from api.conversation.interrupt import Interrupt
from api.conversation.message import QueryMessage


def _sse(data: dict[str, Any] | str) -> str:
    if isinstance(data, str):
        return f"data: {data}\n\n"
    return f"data: {json.dumps(data)}\n\n"


class ConversationUseCase:
    def __init__(
        self,
        date_time: DateTime,
        id_generator: IdGenerator,
    ):
        self.date_time = date_time
        self.id_generator = id_generator

    async def check_active_interrupt(
        self,
        agent_executor: CompiledStateGraph[Any],
        thread_id: str,
        is_resuming: bool,
    ) -> None:
        graph_config: RunnableConfig = {
            "configurable": {
                "thread_id": thread_id,
            }
        }
        snap = await agent_executor.aget_state(graph_config)
        if snap.interrupts and not is_resuming:
            raise WaitingInterrupt()

    async def execute(
        self,
        agent_executor: CompiledStateGraph[Any],
        thread_id: str,
        message: QueryMessage,
    ) -> AsyncGenerator[str, None]:
        step = None
        message_id = self.id_generator.generate_random_id()
        graph_config: RunnableConfig = {
            "configurable": {
                "thread_id": thread_id,
            }
        }

        yield _sse({"type": "start", "messageId": message_id})

        async for step in agent_executor.astream(
            {"messages": [{"role": "user", "content": message.content}]}
            if not message.is_resuming
            else Command(resume=json.loads(message.content)),
            stream_mode="updates",
            config=graph_config,
        ):
            if "tools" in step and "ui" in step["tools"]:
                ui = step["tools"]["ui"]
                yield _sse({"type": "start-step"})
                yield _sse(
                    {
                        "type": f"data-{ui['name']}",
                        "data": {
                            "id": ui["id"],
                            "args": ui["props"],
                        },
                    }
                )
                yield _sse({"type": "finish-step"})

            if Interrupt.is_step_interrupt(step):
                langgraph_interrupt = cast(LanggraphInterrupt, step["__interrupt__"][0])
                interrupt_msg = Interrupt.to_message(
                    langgraph_interrupt,
                    langgraph_interrupt.id,
                    self.date_time.now_str(),
                )
                yield _sse({"type": "start-step"})
                yield _sse(
                    {
                        "type": "data-interrupt",
                        "data": {
                            "id": interrupt_msg.id,
                            "is_interrupting": interrupt_msg.is_interrupting,
                            "ui": {
                                "id": interrupt_msg.ui.id,
                                "args": interrupt_msg.ui.args,
                            }
                            if interrupt_msg.ui
                            else None,
                            "content": interrupt_msg.content,
                        },
                    }
                )
                yield _sse({"type": "finish-step"})
                yield _sse({"type": "finish"})
                yield _sse("[DONE]")
                return

        if not step:
            raise ValueError("No steps returned from the agent executor.")

        last_message = cast(AIMessage | HumanMessage, step["model"]["messages"][-1])
        last_message_text = cast(
            str,
            next((c["text"] for c in last_message.content if c["type"] == "text"), ""),
        )

        text_id = self.id_generator.generate_random_id()
        yield _sse({"type": "start-step"})
        yield _sse({"type": "text-start", "id": text_id})
        yield _sse({"type": "text-delta", "id": text_id, "delta": last_message_text})
        yield _sse({"type": "text-end", "id": text_id})
        yield _sse({"type": "finish-step"})
        yield _sse({"type": "finish"})
        yield _sse("[DONE]")
