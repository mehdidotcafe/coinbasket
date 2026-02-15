import json
from typing import Any
from unittest import mock

from api.conversation.exception.waiting_interrupt import WaitingInterrupt
from api.conversation.message import QueryMessage
from pytest import fixture, mark, raises

from api.conversation.conversation_use_case import (
    ConversationUseCase,
)
from api.datetime.date_time import DateTime
from api.shared.id_generator.id_generator import IdGenerator
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Interrupt


def _parse_sse_chunks(chunks: list[str]) -> list[Any]:
    events: list[Any] = []
    for chunk in chunks:
        line = chunk.strip()
        if line.startswith("data: "):
            payload = line[len("data: ") :]
            try:
                events.append(json.loads(payload))
            except json.JSONDecodeError:
                events.append(payload)
    return events


@fixture
def date_time():
    return mock.Mock(spec=DateTime)


@fixture
def agent_executor():
    return mock.Mock(spec=CompiledStateGraph)


@fixture
def thread_id():
    return "63"


@fixture
def id_generator():
    generator = mock.Mock(spec=IdGenerator)
    generator.generate_random_id.return_value = "random-id"
    return generator


@fixture
def use_case(date_time: DateTime, id_generator: IdGenerator):
    return ConversationUseCase(
        date_time=date_time,
        id_generator=id_generator,
    )


@mark.asyncio
async def test_conversation_use_case_execute_text_only(
    date_time: DateTime,
    use_case: ConversationUseCase,
    thread_id: str,
    agent_executor: CompiledStateGraph,
):
    date_time.now_str = mock.Mock(return_value="2023-10-01")
    message = QueryMessage(
        id="42",
        is_resuming=False,
        role="user",
        content="Hello?",
        created_at="2023-10-01",
    )

    step = {
        "model": {
            "messages": [
                mock.Mock(
                    id="1",
                    content=[{"text": "Hello, how can I help you?", "type": "text"}],
                )
            ]
        }
    }
    agent_executor.astream = mock.MagicMock()
    agent_executor.astream.return_value.__aiter__.return_value = [step]

    chunks = [
        chunk async for chunk in use_case.execute(agent_executor, thread_id, message)
    ]
    events = _parse_sse_chunks(chunks)

    assert events[0]["type"] == "start"
    assert "messageId" in events[0]
    assert events[1] == {"type": "start-step"}
    assert events[2]["type"] == "text-start"
    text_id = events[2]["id"]
    assert events[3] == {
        "type": "text-delta",
        "id": text_id,
        "delta": "Hello, how can I help you?",
    }
    assert events[4] == {"type": "text-end", "id": text_id}
    assert events[5] == {"type": "finish-step"}
    assert events[6] == {"type": "finish"}
    assert events[7] == "[DONE]"


@mark.asyncio
async def test_conversation_use_case_execute_with_ui_then_text(
    date_time: DateTime,
    use_case: ConversationUseCase,
    thread_id: str,
    agent_executor: CompiledStateGraph,
):
    date_time.now_str = mock.Mock(return_value="2023-10-01")
    message = QueryMessage(
        id="42",
        is_resuming=False,
        role="user",
        content="Hello?",
        created_at="2023-10-01",
    )

    steps = [
        {
            "tools": {
                "messages": [mock.Mock()],
                "ui": {
                    "id": "tool_ui_1",
                    "name": "tool_ui",
                    "props": {"key": "value"},
                },
            }
        },
        {
            "model": {
                "messages": [
                    mock.Mock(
                        id="1",
                        content=[
                            {"text": "Hello, how can I help you?", "type": "text"}
                        ],
                    )
                ]
            },
        },
    ]
    agent_executor.astream = mock.MagicMock()
    agent_executor.astream.return_value.__aiter__.return_value = steps

    chunks = [
        chunk async for chunk in use_case.execute(agent_executor, thread_id, message)
    ]
    events = _parse_sse_chunks(chunks)

    assert events[0]["type"] == "start"
    # UI step
    assert events[1] == {"type": "start-step"}
    assert events[2] == {
        "type": "data-tool_ui",
        "data": {"id": "tool_ui_1", "args": {"key": "value"}},
    }
    assert events[3] == {"type": "finish-step"}
    # Text step
    assert events[4] == {"type": "start-step"}
    assert events[5]["type"] == "text-start"
    text_id = events[5]["id"]
    assert events[6] == {
        "type": "text-delta",
        "id": text_id,
        "delta": "Hello, how can I help you?",
    }
    assert events[7] == {"type": "text-end", "id": text_id}
    assert events[8] == {"type": "finish-step"}
    assert events[9] == {"type": "finish"}
    assert events[10] == "[DONE]"


@mark.asyncio
async def test_conversation_use_case_execute_interrupt(
    date_time: DateTime,
    use_case: ConversationUseCase,
    agent_executor: CompiledStateGraph,
    thread_id: str,
):
    date_time.now_str = mock.Mock(return_value="2023-10-01")
    message = QueryMessage(
        id="42",
        is_resuming=False,
        role="user",
        content="Hello?",
        created_at="2023-10-01",
    )

    step = {
        "__interrupt__": (
            Interrupt(
                value={
                    "ui": {
                        "id": "prepare_investment_plan",
                        "args": {
                            "intent_investment_plan": {
                                "steps": [
                                    {"buy_balance": None, "sell_balance": None},
                                    {"buy_balance": None, "sell_balance": None},
                                ]
                            }
                        },
                    },
                    "content": None,
                },
                id="99",
                resumable=True,
                ns=["tools:43e88f20-5846-1931-5515-951101740e44"],
            ),
        )
    }

    agent_executor.astream = mock.MagicMock()
    agent_executor.astream.return_value.__aiter__.return_value = [step]

    chunks = [
        chunk async for chunk in use_case.execute(agent_executor, thread_id, message)
    ]
    events = _parse_sse_chunks(chunks)

    assert events[0]["type"] == "start"
    assert events[1] == {"type": "start-step"}
    assert events[2]["type"] == "data-interrupt"
    assert events[2]["data"]["id"] == "99"
    assert events[2]["data"]["is_interrupting"] is True
    assert events[2]["data"]["ui"]["id"] == "prepare_investment_plan"
    assert events[2]["data"]["content"] is None
    assert events[3] == {"type": "finish-step"}
    assert events[4] == {"type": "finish"}
    assert events[5] == "[DONE]"


@mark.asyncio
async def test_conversation_use_case_check_active_interrupt_raises(
    use_case: ConversationUseCase,
    agent_executor: CompiledStateGraph,
    thread_id: str,
):
    snap_mock = mock.Mock()
    snap_mock.interrupts = [mock.Mock()]
    agent_executor.aget_state = mock.AsyncMock(return_value=snap_mock)

    with raises(WaitingInterrupt):
        await use_case.check_active_interrupt(
            agent_executor, thread_id, is_resuming=False
        )


@mark.asyncio
async def test_check_active_interrupt_allows_resume(
    use_case: ConversationUseCase,
    agent_executor: CompiledStateGraph,
    thread_id: str,
):
    snap_mock = mock.Mock()
    snap_mock.interrupts = [mock.Mock()]
    agent_executor.aget_state = mock.AsyncMock(return_value=snap_mock)

    await use_case.check_active_interrupt(agent_executor, thread_id, is_resuming=True)


@mark.asyncio
async def test_execute_filters_out_tools_without_ui(
    date_time: DateTime,
    use_case: ConversationUseCase,
    thread_id: str,
    agent_executor: CompiledStateGraph,
):
    date_time.now_str = mock.Mock(return_value="2023-10-01")
    message = QueryMessage(
        id="42",
        is_resuming=False,
        role="user",
        content="Hello?",
        created_at="2023-10-01",
    )

    steps = [
        {
            "tools": {
                "messages": [mock.Mock()],
            }
        },
        {
            "model": {
                "messages": [
                    mock.Mock(
                        id="1",
                        content=[{"text": "Done", "type": "text"}],
                    )
                ]
            },
        },
    ]
    agent_executor.astream = mock.MagicMock()
    agent_executor.astream.return_value.__aiter__.return_value = steps

    chunks = [
        chunk async for chunk in use_case.execute(agent_executor, thread_id, message)
    ]
    events = _parse_sse_chunks(chunks)

    # Should only have: start, start-step, text-start, text-delta, text-end, finish-step, finish, [DONE]
    assert len(events) == 8
    assert events[0]["type"] == "start"
    assert events[1] == {"type": "start-step"}
    assert events[2]["type"] == "text-start"
    assert events[6] == {"type": "finish"}
