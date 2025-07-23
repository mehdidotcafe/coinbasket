from unittest import mock
from invest_agent.conversation.message import Message, MessageUi, QueryMessage
from pytest import fixture, mark

from invest_agent.conversation.conversation_use_case import (
    ConversationUseCase,
)
from invest_agent.datetime.date_time import DateTime
from langgraph.graph.graph import CompiledGraph
from langgraph.types import Interrupt
from shared.id_generator.id_generator import IdGenerator


@fixture
def date_time():
    return mock.Mock(spec=DateTime)


@fixture
def agent_executor():
    return mock.Mock(spec=CompiledGraph)


@fixture
def id_generator():
    return mock.Mock(spec=IdGenerator)


@fixture
def use_case(date_time: DateTime, id_generator: IdGenerator):
    return ConversationUseCase(
        date_time=date_time,
        id_generator=id_generator,
        configuration={"langchain_thread_id": "63"},
    )


@mark.asyncio
async def test_conversation_use_case_execute_agent_last_step(
    date_time: DateTime,
    use_case: ConversationUseCase,
    agent_executor: CompiledGraph,
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
        "agent": {"messages": [mock.Mock(id="1", content="Hello, how can I help you?")]}
    }
    agent_executor.astream = mock.MagicMock()
    agent_executor.astream.return_value.__aiter__.return_value = [step]

    message = await use_case.execute(agent_executor, message)

    assert message == Message(
        id="1",
        role="assistant",
        is_interrupting=False,
        ui=None,
        content="Hello, how can I help you?",
        created_at="2023-10-01",
    )


@mark.asyncio
async def test_conversation_use_case_execute_interrupt_last_step(
    date_time: DateTime,
    use_case: ConversationUseCase,
    agent_executor: CompiledGraph,
    id_generator: IdGenerator,
):
    id_generator.generate_random_id = mock.Mock(return_value="99")
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
                resumable=True,
                ns=["tools:43e88f20-5846-1931-5515-951101740e44"],
            ),
        )
    }
    agent_executor.astream = mock.MagicMock()
    agent_executor.astream.return_value.__aiter__.return_value = [step]

    message = await use_case.execute(agent_executor, message)

    assert message == Message(
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
