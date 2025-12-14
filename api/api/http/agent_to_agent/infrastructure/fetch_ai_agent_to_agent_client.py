from uagents import Agent, Model
from typing import TypeVar, TypedDict, cast
from aiohttp import ClientSession
from uagents.communication import send_message

from api.http.agent_to_agent.agent_to_agent_client import AgentToAgentClient

U = TypeVar("U", bound=Model)


class Configuration(TypedDict):
    data_agent_address: str


class FetchAiAgentToAgentClient(AgentToAgentClient):
    """
    Aiohttp implementation of the AgentToAgentClient interface.
    """

    def __init__(
        self,
        configuration: Configuration,
        agent: Agent,
        aiohttp_client_session: type[ClientSession],
    ):
        self.aiohttp_client_session = aiohttp_client_session
        self.configuration = configuration
        self.agent = agent

    async def send_and_receive_message(
        self, message: Model, response_model: type[U]
    ) -> U:
        """
        Send a message to another agent using aiohttp.
        """
        res = await send_message(
            destination=self.configuration["data_agent_address"],
            message=message,
            response_type=cast(type[Model], response_model),
            sender=self.agent._identity,
        )

        if not isinstance(res, response_model):
            raise ValueError("Response is None.")

        return res
