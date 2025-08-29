from unittest import mock
from pytest import fixture, mark

from invest_agent.conversation.repository.conversation_repository import (
    ConversationRepository,
)
from invest_agent.conversation.get_conversation_messages_use_case import (
    GetConversationMessagesUseCase,
)
from invest_agent.conversation.message import Message

from langgraph.graph.state import CompiledStateGraph


@fixture
def conversation_repository():
    return mock.Mock(spec=ConversationRepository)


@fixture
def agent_executor():
    return mock.Mock(spec=CompiledStateGraph)


@mark.asyncio
async def test_get_conversation_messages_use_case(
    conversation_repository: ConversationRepository,
    agent_executor: CompiledStateGraph,
):
    thread_id = "test_thread_id"
    messages = [
        Message(
            id="1",
            is_interrupting=False,
            ui=None,
            role="user",
            content="Hello, how are you?",
            created_at="2023-10-01T12:00:00Z",
        ),
        Message(
            id="2",
            is_interrupting=False,
            ui=None,
            role="assistant",
            content="Hello, how are you?",
            created_at="2023-10-01T12:00:00Z",
        ),
    ]
    interrupts = [
        Message(
            id="3",
            is_interrupting=True,
            ui="{'id': 'interrupting_message'}",
            role="user",
            content=None,
            created_at="2023-10-01T12:00:00Z",
        ),
    ]

    conversation_repository.get_messages.return_value = messages
    conversation_repository.get_interrupts.return_value = interrupts

    use_case = GetConversationMessagesUseCase(conversation_repository)

    result = await use_case.execute(thread_id, agent_executor)

    assert result == messages + interrupts
    conversation_repository.get_messages.assert_called_once_with(thread_id)
    conversation_repository.get_interrupts.assert_called_once_with(
        thread_id, agent_executor
    )
