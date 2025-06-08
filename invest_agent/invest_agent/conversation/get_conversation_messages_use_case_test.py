from unittest import mock
from pytest import fixture, mark

from invest_agent.conversation.repository.conversation_repository import (
    ConversationRepository,
)
from invest_agent.conversation.get_conversation_messages_use_case import (
    GetConversationMessagesUseCase,
)
from invest_agent.conversation.message import Message


@fixture
def conversation_repository():
    return mock.Mock(spec=ConversationRepository)


@mark.asyncio
async def test_get_conversation_messages_use_case(
    conversation_repository: ConversationRepository,
):
    thread_id = "test_thread_id"
    messages = [
        Message(
            id="1",
            role="user",
            content="Hello, how are you?",
            created_at="2023-10-01T12:00:00Z",
        ),
        Message(
            id="2",
            role="assistant",
            content="Hello, how are you?",
            created_at="2023-10-01T12:00:00Z",
        ),
    ]
    conversation_repository.get_messages.return_value = messages

    use_case = GetConversationMessagesUseCase(conversation_repository)

    result = await use_case.execute(thread_id)

    assert result == messages
    conversation_repository.get_messages.assert_called_once_with(thread_id)
