from pydantic import BaseModel
from shared.http_request.infrastructure.aiohttp_http_request import AiohttpHttpRequest
from uagents import Model
from typing import Type, TypeVar, TypedDict, cast

from api.http.agent_to_agent.agent_to_agent_client import AgentToAgentClient

U = TypeVar("U", bound=Model)


class Configuration(TypedDict):
    agent_url: str


class AiohttpAgentToAgentClient(AgentToAgentClient):
    """
    Aiohttp implementation of the AgentToAgentClient interface.
    """

    def __init__(
        self, configuration: Configuration, aiohttp_http_request: AiohttpHttpRequest
    ):
        self.configuration = configuration
        self.aiohttp_http_request = aiohttp_http_request

    async def send_and_receive_message(
        self, message: Model, response_model: Type[U], key: str = ""
    ) -> U:
        """
        Send a message to another agent using aiohttp.
        """
        return cast(
            U,
            await self.aiohttp_http_request.post(
                {
                    "url": f"{self.configuration['agent_url']}{key}",
                    "headers": {"Content-Type": "application/json"},
                    "body": message.model_dump(),
                },
                cast(Type[BaseModel], response_model),
            ),
        )
