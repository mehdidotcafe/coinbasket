from invest_agent.conversation.repository.conversation_repository import ConversationRepository
from invest_agent.conversation.message import Message


class GetConversationMessagesUseCase:
    def __init__(self, conversation_repository: ConversationRepository):
        self.conversation_repository = conversation_repository

    async def execute(self, thread_id: str) -> list[Message]:
        messages = await self.conversation_repository.get_messages(thread_id)

        return messages
