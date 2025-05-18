from uagents import Model
from typing import TypeVar, TypedDict
from aiohttp import ClientSession

from invest_agent.http.agent_to_agent.agent_to_agent_client import AgentToAgentClient

U = TypeVar("U", bound=Model)


class Configuration(TypedDict):
    agent_url: str


class AiohttpAgentToAgentClient(AgentToAgentClient):
    """
    Aiohttp implementation of the AgentToAgentClient interface.
    """

    def __init__(
        self, configuration: Configuration, aiohttp_client_session: type[ClientSession]
    ):
        self.aiohttp_client_session = aiohttp_client_session
        self.configuration = configuration

    async def send_and_receive_message(
        self, message: Model, response_model: type[U]
    ) -> U:
        """
        Send a message to another agent using aiohttp.
        """
        async with self.aiohttp_client_session() as session:
            async with session.post(
                self.configuration["agent_url"],
                headers={"Content-Type": "application/json"},
                data=message.json(),
            ) as response:
                res = await response.json()
                validated_res = response_model.model_validate(res)

                return validated_res
