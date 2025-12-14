from abc import ABC, abstractmethod

from uagents import Model


class AgentToAgentClient(ABC):
    @abstractmethod
    async def send_and_receive_message(
        self, message: Model, response_model: type[Model], key: str
    ) -> Model:
        raise NotImplementedError
