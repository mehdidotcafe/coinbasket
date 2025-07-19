from unittest import mock
from invest_agent.conversation.message import Message
from pytest import fixture, mark

from invest_agent.conversation.conversation_use_case import (
    ConversationUseCase,
)
from invest_agent.datetime.date_time import DateTime
from langgraph.graph.graph import CompiledGraph


@fixture
def date_time():
    return mock.Mock(spec=DateTime)


@fixture
def agent_executor():
    return mock.Mock(spec=CompiledGraph)


@fixture
def use_case(date_time: DateTime):
    return ConversationUseCase(
        date_time=date_time,
        configuration={"langchain_thread_id": "63"},
    )


@mark.asyncio
async def test_conversation_use_case_execute_agent_last_step(
    date_time: DateTime,
    use_case: ConversationUseCase,
    agent_executor: CompiledGraph,
):
    date_time.now_str = mock.Mock(return_value="2023-10-01")
    message = Message(
        id="42",
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
        content="Hello, how can I help you?",
        created_at="2023-10-01",
    )


@mark.asyncio
async def test_conversation_use_case_execute_tool_last_step(
    date_time: DateTime,
    use_case: ConversationUseCase,
    agent_executor: CompiledGraph,
):
    date_time.now_str = mock.Mock(return_value="2023-10-01")
    message = Message(
        id="42",
        role="user",
        content="Hello?",
        created_at="2023-10-01",
    )

    step = {
        "tools": {
            "messages": [
                mock.Mock(id="1", content='{"tool": "prepare_investment_plan"}')
            ]
        }
    }
    agent_executor.astream = mock.MagicMock()
    agent_executor.astream.return_value.__aiter__.return_value = [step]

    message = await use_case.execute(agent_executor, message)

    assert message == Message(
        id="1",
        role="tool",
        content='{"tool": "prepare_investment_plan"}',
        created_at="2023-10-01",
    )
