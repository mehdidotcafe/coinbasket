from unittest import mock
from api.conversation.exception.waiting_interrupt import WaitingInterrupt
from api.conversation.message import Message, MessageUi, QueryMessage
from pytest import fixture, mark, raises

from api.conversation.conversation_use_case import (
    ConversationUseCase,
)
from api.datetime.date_time import DateTime
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Interrupt


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
def use_case(date_time: DateTime):
    return ConversationUseCase(
        date_time=date_time,
    )


@mark.asyncio
async def test_conversation_use_case_execute_agent_last_step_no_ui(
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
    agent_executor.aget_state = mock.AsyncMock(return_value=mock.Mock(interrupts=[]))
    agent_executor.astream = mock.MagicMock()
    agent_executor.astream.return_value.__aiter__.return_value = [step]

    message = await use_case.execute(agent_executor, thread_id, message)

    assert message == [
        Message(
            id="1",
            role="assistant",
            is_interrupting=False,
            ui=None,
            content="Hello, how can I help you?",
            created_at="2023-10-01",
        )
    ]


@mark.asyncio
async def test_conversation_use_case_execute_agent_last_step_ui(
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
    agent_executor.aget_state = mock.AsyncMock(return_value=mock.Mock(interrupts=[]))
    agent_executor.astream = mock.MagicMock()
    agent_executor.astream.return_value.__aiter__.return_value = steps

    message = await use_case.execute(agent_executor, thread_id, message)

    assert message == [
        Message(
            id="tool_ui_1",
            role="assistant",
            is_interrupting=False,
            ui=MessageUi(id="tool_ui", args={"key": "value"}),
            content=None,
            created_at="2023-10-01",
        ),
        Message(
            id="1",
            role="assistant",
            is_interrupting=False,
            ui=None,
            content="Hello, how can I help you?",
            created_at="2023-10-01",
        ),
    ]


@mark.asyncio
async def test_conversation_use_case_execute_interrupt_last_step(
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

    agent_executor.aget_state = mock.AsyncMock(return_value=mock.Mock(interrupts=[]))
    agent_executor.astream = mock.MagicMock()
    agent_executor.astream.return_value.__aiter__.return_value = [step]

    message = await use_case.execute(agent_executor, thread_id, message)

    assert message == [
        Message(
            id="99",
            role="assistant",
            content=None,
            is_interrupting=True,
            ui=MessageUi(
                id="prepare_investment_plan",
                args={
                    "intent_investment_plan": {
                        "steps": [
                            {"buy_balance": None, "sell_balance": None},
                            {"buy_balance": None, "sell_balance": None},
                        ]
                    }
                },
            ),
            created_at="2023-10-01",
        )
    ]


async def test_conversation_use_case_execute_with_active_interrupt_raises(
    use_case: ConversationUseCase,
    agent_executor: CompiledStateGraph,
    thread_id: str,
):
    message = QueryMessage(
        id="42",
        is_resuming=False,
        role="user",
        content="Hello?",
        created_at="2023-10-01",
    )

    snap_mock = mock.Mock()
    snap_mock.interrupts = [mock.Mock()]

    agent_executor.aget_state = mock.AsyncMock(return_value=snap_mock)

    with raises(WaitingInterrupt):
        await use_case.execute(agent_executor, thread_id, message)
