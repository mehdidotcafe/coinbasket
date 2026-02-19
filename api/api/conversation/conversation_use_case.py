import json
from collections.abc import AsyncGenerator
from typing import Any, cast

from langgraph.types import Command

from api.conversation.exception.waiting_interrupt import WaitingInterrupt
from api.datetime.date_time import DateTime
from api.shared.id_generator.id_generator import IdGenerator
from langchain_core.messages import AIMessageChunk
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
        text_started = False
        text_id = None
        message_id = self.id_generator.generate_random_id()
        graph_config: RunnableConfig = {
            "configurable": {
                "thread_id": thread_id,
            }
        }

        yield _sse({"type": "start", "messageId": message_id})

        async for mode, data in agent_executor.astream(
            {"messages": [{"role": "user", "content": message.content}]}
            if not message.is_resuming
            else Command(resume=json.loads(message.content)),
            stream_mode=["updates", "messages"],
            config=graph_config,
        ):
            # print(f"Received from agent executor - mode: {mode}, data: {data}")

            if mode == "messages":
                chunk, _metadata = data
                if not isinstance(chunk, AIMessageChunk):
                    continue
                tokens = self._extract_tokens_from_chunk(chunk)
                if not text_started:
                    text_id = self.id_generator.generate_random_id()
                    yield _sse({"type": "start-step"})
                    yield _sse({"type": "text-start", "id": text_id})
                    text_started = True
                for token in tokens:
                    yield _sse({"type": "text-delta", "id": text_id, "delta": token})

            elif mode == "updates":
                if "tools" in data and "ui" in data["tools"]:
                    ui = data["tools"]["ui"]
                    yield _sse({"type": "start-step"})
                    text_started = True
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
                    text_started = False

                if Interrupt.is_step_interrupt(data):
                    langgraph_interrupt = cast(
                        LanggraphInterrupt, data["__interrupt__"][0]
                    )
                    interrupt_msg = Interrupt.to_message(
                        langgraph_interrupt,
                        langgraph_interrupt.id,
                        self.date_time.now_str(),
                    )
                    yield _sse({"type": "start-step"})
                    text_started = True
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
                    text_started = False

                if "model" in data:
                    if text_started:
                        yield _sse({"type": "text-end", "id": text_id})
                        yield _sse({"type": "finish-step"})
                        text_started = False

        yield _sse({"type": "finish"})
        yield _sse("[DONE]")

    def _extract_tokens_from_chunk(self, chunk: AIMessageChunk) -> list[str]:
        if isinstance(chunk.content, str):
            return [chunk.content]

        tokens: list[str] = []
        for item in chunk.content:
            if isinstance(item, str):
                tokens.append(item)
            elif "text" in item and isinstance(item["text"], str):
                tokens.append(item["text"])
        return tokens
