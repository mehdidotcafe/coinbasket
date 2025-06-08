import os
from typing import Any, Dict, Optional, cast

import aiohttp
from apispec import APISpec
from invest_agent.authentication.authentication import authentication
from invest_agent.conversation.get_conversation_messages_use_case import (
    GetConversationMessagesUseCase,
)
from invest_agent.conversation.repository.infrastructure.langchain_sqlite_conversation_repository import (
    LangchainSqliteConversationRepository,
)
from invest_agent.datetime.infrastructure.python_date_time import PythonDateTime
from invest_agent.documentation.response.invalid_authentication_key import (
    invalid_authentication_key,
)
from invest_agent.http.agent_to_agent.infrastructure.aiohttp_agent_to_agent_client import (
    AiohttpAgentToAgentClient,
)
from invest_agent.http_request.infrastructure.requests_http_request import (
    RequestsHttpRequest,
)
from invest_agent.investment.basket_investment import BasketInvestment
from invest_agent.investment.infrastructure.zero_x.zero_x_api_client import (
    ZeroXApiClient,
)
from invest_agent.investment.infrastructure.zero_x.zero_x_swapper import ZeroXSwapper
from invest_agent.metrics.get_wallet_in_token_use_case import (
    GetWalletInTokenUseCase,
)
from invest_agent.documentation.openapi import openapi
from protocol.basket import Basket
from protocol.token import Token
from pydantic import RootModel
from uagents import Agent, Context, Model
from uagents.storage import KeyValueStore

import aiosqlite

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from web3 import AsyncWeb3, AsyncHTTPProvider

from invest_agent.infrastructure.bsc.chain.bsc_chain import BscChain
from invest_agent.configuration import Configuration
from invest_agent.investment.basket_divest_use_case import BasketDivestUseCase
from invest_agent.investment.divestment_planner_strategy.total_divestment_planner import (
    TotalDivestmentPlanner,
)
from invest_agent.investment.get_basket_investment_use_case import (
    GetBasketInvestmentUseCase,
)
from invest_agent.investment.basket_invest_use_case import BasketInvestUseCase
from invest_agent.investment.investment_planner_strategy.equal_investment_planner import (
    EqualInvestmentPlanner,
)
from invest_agent.infrastructure.fetch_ai.storage.fetch_ai_storage import (
    FetchAiStorage,
)

from protocol import SimilarityQuery, SimilarityResponse
from protocol.fixture.token import usdt_token

date_time = PythonDateTime()


configuration = Configuration()

print(f"Thread ID: {configuration.langchain_thread_id}")


if configuration.langsmith_tracing:
    os.environ["LANGSMITH_TRACING"] = str(configuration.langsmith_tracing)
    os.environ["LANGSMITH_API_KEY"] = configuration.langsmith_api_key
    os.environ["LANGSMITH_PROJECT"] = configuration.langsmith_project


spec = APISpec(
    title=configuration.agent_name,
    version="0.0.1",
    openapi_version="3.0.2",
)

invest_agent = Agent(
    name=configuration.agent_name,
    seed=configuration.agent_seed,
    port=configuration.agent_port,
    endpoint=f"http://localhost:{configuration.agent_port}/submit",
)

w3 = AsyncWeb3(AsyncHTTPProvider(configuration.bsc_rpc_url))

chain = BscChain(w3=w3, private_key=configuration.bsc_private_key)

http_request = RequestsHttpRequest[Any]()

api_client = ZeroXApiClient(
    configuration={
        "zero_x_api_url": configuration.zero_x_api_url,
        "zero_x_api_key": configuration.zero_x_api_key,
    },
    http_request=http_request,
)

exchange = ZeroXSwapper(
    api_client=api_client,
    chain=chain,
    w3=w3,
    configuration={
        "bsc_rpc_url": configuration.bsc_rpc_url,
        "private_key": configuration.bsc_private_key,
    },
)
storage = FetchAiStorage[Any](
    configuration.langchain_thread_id,
    store=KeyValueStore(configuration.agent_name, "./database"),
)
agent_to_agent_client = AiohttpAgentToAgentClient(
    configuration={"agent_url": configuration.data_agent_url},
    aiohttp_client_session=aiohttp.ClientSession,
)

basket_invest_use_case = BasketInvestUseCase(
    investment_planner=EqualInvestmentPlanner(chain),
    exchange=exchange,
    storage=storage,
    date_time=date_time,
)
basket_divest_use_case = BasketDivestUseCase(
    divestment_planner=TotalDivestmentPlanner(chain),
    exchange=exchange,
    storage=storage,
    date_time=date_time,
    chain=chain,
    configuration={
        "fee_integrator_address": configuration.fee_integrator_address,
        "fee_value_in_percentage": configuration.fee_value_in_percentage,
    },
)
get_basket_investment_use_case = GetBasketInvestmentUseCase(storage=storage)

get_basket_balance_in_token_use_case = GetWalletInTokenUseCase(
    storage=storage,
    exchange=exchange,
    chain=chain,
    configuration={
        "fee_integrator_address": configuration.fee_integrator_address,
        "fee_value_in_percentage": configuration.fee_value_in_percentage,
    },
)


conversation_repository = LangchainSqliteConversationRepository(
    db_path="./database/langchain_graphs.db", date_time=date_time
)

get_conversation_messages_use_case = GetConversationMessagesUseCase(
    conversation_repository=conversation_repository
)


@tool(response_format="content_and_artifact")
async def get_token_info(query: str):
    """
    Retrieve a list of available tokens / coins to invest or.

    Args:
        query: The query to search for.

    Returns:
        A list of documents containing tokens / coins.
        Each token has a name, display_name, ticker and address (contract address) property.
    """

    # TODO: Use fetch ai send_and_receive when fixed with multiple concurrent requests
    res = await agent_to_agent_client.send_and_receive_message(
        SimilarityQuery(
            query=f"{query} type:token", agent_key=configuration.data_agent_key
        ),
        SimilarityResponse,
    )

    if isinstance(res.data, str):
        raise ValueError(f"Response is not a valid response: {res.data}")

    return res.data.serialized, res.data.retrieved_docs


@tool(response_format="content_and_artifact")
async def get_preset_basket_info(query: str):
    """
    Retrieve a list of available preset baskets to invest in.

    Args:
        query: The query to search for.

    Returns:
        A list of documents containing available preset baskets.
        Each basket is made of a name, a description and a list of tokens.
        Each token has a name, display_name, ticker and address (contract address) property.
    """

    # TODO: Use fetch ai send_and_receive when fixed with multiple concurrent requests
    res = await agent_to_agent_client.send_and_receive_message(
        SimilarityQuery(
            query=f"{query} type:basket", agent_key=configuration.data_agent_key
        ),
        SimilarityResponse,
    )

    if isinstance(res.data, str):
        raise ValueError(f"Response is not a valid response: {res.data}")

    return res.data.serialized, res.data.retrieved_docs


@tool()
def get_address():
    """Retrieve agent's current wallet address."""
    return chain.get_address()


@tool()
async def get_balance(query: str):
    """Retrieve agent's current wallet balance in BNB."""
    print("IN get_balance")
    print(f"Query: {query}")

    return await chain.get_balance()


@tool()
def get_invested_basket():
    """Retrieve the invested basket in native value only.

    Returns:
        The invested basket made of the bids that were made by the agent when investing in the basket.
        Each bid has a token and a balance_in and balance_out property.
        The token has a name, display_name, ticker and address (contract address) property.
    """
    return get_basket_investment_use_case.execute()


@tool()
async def get_invested_basket_balance_in_native_and_usd_value():
    """Retrieve the invested basket in native and USD Value.

    Returns:
        The basket balance is made of the balances of each token in the basket, both in native and USD value.
        The token has a name, display_name, ticker and address (contract address) property.
    """
    return await get_basket_balance_in_token_use_case.execute(usdt_token)


@tool(response_format="content_and_artifact")
async def invest_basket(basket: Basket):
    """Invest / fund / buy the basket created by the user by spending all the available BNB in the agent's wallet.
    Each basket coin needs to have a name, ticker and address.
    A basket can't be invested if it already has been invested.
    Always ask for user confirmation before investing in the basket.

    Args:
        basket: The basket to Invest / fund / buy.

    Returns:
        BasketInvestment: The basket investment made of the bids that were made by the agent when investing in the basket.
    """
    message, basket_investment = await basket_invest_use_case.execute(basket)

    if basket_investment is None:
        return message, None

    content: Dict[str, str | BasketInvestment] = {
        "message": message,
        "basket_investment": basket_investment,
    }

    return content, basket_investment


@tool()
async def divest_basket():
    """Divest / sell the whole basket create by the user.
    This tool cannot be used if the basket has not been invested yet.
    This tool cannot be used if to divest just a part of the basket, it divests the whole basket.
    Always ask for user confirmation before divesting the basket.

    Args:
        basket: The basket to Invest / fund / buy.
    """
    return await basket_divest_use_case.execute()


llm = init_chat_model(
    model=configuration.chat_model,
    model_provider=configuration.chat_provider,
    api_key=configuration.chat_provider_api_key,
)


def create_agent_executor(conn: aiosqlite.Connection):
    sqliteMemory = AsyncSqliteSaver(conn)

    agent_executor = create_react_agent(
        llm,
        [
            get_preset_basket_info,
            get_token_info,
            invest_basket,
            get_address,
            get_balance,
            get_invested_basket,
            get_invested_basket_balance_in_native_and_usd_value,
            divest_basket,
        ],
        checkpointer=sqliteMemory,
        prompt=SystemMessage(
            f"Your name is {configuration.agent_name}.  "
            "Your goal is to create and then invest in crypto coin baskets. You can invest in a single coin by creating a basket with a single coin.  "
            # "You operate only on the Binance Smart Chain (BSC) network.  "
            f"Today is {date_time.now_str()}.  "
            "Always give a name and a description to the basket you are creating. Reevaluate them after each update.  "
            "Always show the user the basket you are creating by showing its name and listing the coins in a single list with the coin display name, ticker and address. Don't mention excluded coins.  "
            "When you display a token or coin, always show its address as a link using this link 'https://bscscan.com/token/[token_address]'.  "
            "After each answer, ask the user if he wants to add or remove any coins from the basket or if he wants to invest in the basket.  "
            "Always ask for the user's confirmation before investing in the basket and show a message mentioning that he should do his own research (DYOR) before investing.  "
            "Always ask for the user's confirmation before divesting the basket. "
            "Always use get_preset_basket_info to retrieve the list of available preset baskets to invest in.  "
            "Always use get_token_info to retrieve the list of available tokens / coins.  "
            "You can't manage more than one basket.  "
            "If you don't know the answer, just say that you don't know and mention what you can do, don't try to make up an answer.  "
        ),
    )

    return agent_executor


class MessageRequest(Model):
    id: str
    role: str
    content: str
    created_at: Optional[str]


class PromptRequest(Model):
    message: MessageRequest
    agent_key: str


class MessageResponse(Model):
    id: str
    role: str
    content: str
    created_at: Optional[str]


@openapi(
    spec=spec,
    schemas=[MessageRequest, PromptRequest, MessageResponse],
    path="/conversation",
    operations={
        "post": {
            "summary": "Send message to the Agent",
            "tags": ["Conversation"],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/PromptRequest"}
                    }
                },
            },
            "responses": {
                "200": {
                    "description": "Agent response message",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/MessageResponse"},
                        }
                    },
                },
                "500": invalid_authentication_key,
            },
        }
    },
)
@invest_agent.on_rest_post("/conversation", PromptRequest, MessageResponse)
@authentication(configuration.agent_key)
async def conversation(_ctx: Context, req: PromptRequest) -> MessageResponse:
    async with aiosqlite.connect("./database/langchain_graphs.db") as conn:
        agent_executor = create_agent_executor(conn)

        graph_config: RunnableConfig = {
            "configurable": {
                "thread_id": configuration.langchain_thread_id,
            }
        }

        async for step in agent_executor.astream(
            {"messages": [{"role": "user", "content": req.message.content}]},
            stream_mode="values",
            config=graph_config,
        ):
            step["messages"][-1].pretty_print()

        last_message = step["messages"][-1]

        return MessageResponse(
            id=cast(str, last_message.id),
            role=isinstance(last_message, HumanMessage) and "user" or "assistant",
            content=cast(str, last_message.content),
            created_at=date_time.now_str(),
        )


class MessagesRequest(Model):
    agent_key: str


class MessagesResponse(Model):
    messages: list[MessageResponse]


@openapi(
    spec=spec,
    schemas=[MessagesRequest],
    path="/conversation/messages",
    operations={
        "post": {
            "summary": "Get Agent messages history",
            "tags": ["Conversation"],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/MessagesRequest"}
                    }
                },
            },
            "responses": {
                "200": {
                    "description": "Agent message history",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "array",
                                "items": {
                                    "$ref": "#/components/schemas/MessageResponse"
                                },
                            },
                        }
                    },
                },
                "500": invalid_authentication_key,
            },
        }
    },
)
@invest_agent.on_rest_post("/conversation/messages", MessagesRequest, MessagesResponse)
@authentication(configuration.agent_key)
async def get_conversation_messages(
    _ctx: Context,
    _req: MessagesRequest,
) -> MessagesResponse:
    """Retrieve the conversation messages."""
    messages = await get_conversation_messages_use_case.execute(
        thread_id=configuration.langchain_thread_id
    )

    return MessagesResponse(
        messages=[
            MessageResponse(
                id=message.id,
                role=message.role,
                content=message.content,
                created_at=message.created_at,
            )
            for message in messages
        ]
    )


class AuthRequest(Model):
    agent_key: str


class AuthResponse(Model):
    status: str


@openapi(
    spec=spec,
    schemas=[AuthRequest, AuthResponse],
    path="/auth",
    operations={
        "post": {
            "summary": "Test authentication to the Agent",
            "tags": ["Authentication"],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/AuthRequest"}
                    }
                },
            },
            "responses": {
                "200": {
                    "description": "Authentication status",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/AuthResponse"}
                        }
                    },
                },
                "500": invalid_authentication_key,
            },
        }
    },
)
@invest_agent.on_rest_post("/auth", AuthRequest, AuthResponse)
@authentication(configuration.agent_key)
async def auth_request(_ctx: Context, _req: AuthRequest) -> AuthResponse:
    return AuthResponse(status="OK")


class HealthResponse(Model):
    status: str


@openapi(
    spec=spec,
    schemas=[HealthResponse],
    path="/health",
    operations={
        "get": {
            "summary": "Get agent health",
            "tags": ["Health"],
            "responses": {
                "200": {
                    "description": "Agent health status",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/HealthResponse"}
                        }
                    },
                }
            },
        }
    },
)
@invest_agent.on_rest_get("/health", HealthResponse)
async def health_check(_ctx: Context) -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="OK")


class TokenRequest(Model):
    name: str
    display_name: str
    ticker: str
    address: str


class TokenResponse(Model):
    name: str
    display_name: str
    ticker: str
    address: str


class BalanceResponse(Model):
    amount: str
    token: TokenResponse


class ConvertedBalanceResponse(Model):
    sell_balance: BalanceResponse
    buy_balance: BalanceResponse


class MetricsWalletRequest(Model):
    agent_key: str
    token: TokenRequest


class MetricsWalletResponse(Model):
    balances: list[ConvertedBalanceResponse]
    total_balance: BalanceResponse


@openapi(
    spec=spec,
    schemas=[
        TokenRequest,
        TokenResponse,
        BalanceResponse,
        ConvertedBalanceResponse,
        MetricsWalletRequest,
        MetricsWalletResponse,
    ],
    path="/wallet/token",
    operations={
        "post": {
            "summary": "Get Agent wallet token and total balances in a specific token",
            "tags": ["Wallet"],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/MetricsWalletRequest"}
                    }
                },
            },
            "responses": {
                "200": {
                    "description": "Agent wallet token balances and total balance in the specified token",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "array",
                                "items": {
                                    "$ref": "#/components/schemas/MetricsWalletResponse"
                                },
                            },
                        }
                    },
                },
                "500": invalid_authentication_key,
            },
        }
    },
)
@invest_agent.on_rest_post(
    "/wallet/token",
    MetricsWalletRequest,
    MetricsWalletResponse,
)
@authentication(configuration.agent_key)
async def get_wallet_in_token(_ctx: Context, req: MetricsWalletRequest):
    converted_token_balances = await get_basket_balance_in_token_use_case.execute(
        Token(
            name=req.token.name,
            display_name=req.token.display_name,
            ticker=req.token.ticker,
            address=req.token.address,
        )
    )

    return MetricsWalletResponse(
        balances=[
            ConvertedBalanceResponse(
                sell_balance=BalanceResponse(
                    amount=str(balance.sell_balance.amount),
                    token=TokenResponse(
                        name=balance.sell_balance.token.name,
                        display_name=balance.sell_balance.token.display_name,
                        ticker=balance.sell_balance.token.ticker,
                        address=balance.sell_balance.token.address,
                    ),
                ),
                buy_balance=BalanceResponse(
                    amount=str(balance.buy_balance.amount),
                    token=TokenResponse(
                        name=balance.buy_balance.token.name,
                        display_name=balance.buy_balance.token.display_name,
                        ticker=balance.buy_balance.token.ticker,
                        address=balance.buy_balance.token.address,
                    ),
                ),
            )
            for balance in converted_token_balances.balances
        ],
        total_balance=BalanceResponse(
            amount=str(converted_token_balances.total_balance.amount),
            token=TokenResponse(
                name=converted_token_balances.total_balance.token.name,
                display_name=converted_token_balances.total_balance.token.display_name,
                ticker=converted_token_balances.total_balance.token.ticker,
                address=converted_token_balances.total_balance.token.address,
            ),
        ),
    )


class OpenApiResponse(RootModel[dict[str, Any]]):
    pass


@openapi(
    spec=spec,
    schemas=[OpenApiResponse],
    path="/openapi",
    operations={
        "get": {
            "summary": "Generate JSON OpenAPI documentation",
            "tags": ["Documentation"],
            "responses": {
                "200": {
                    "description": "JSON OpenAPI documentation",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/OpenApiResponse"},
                        }
                    },
                },
            },
        }
    },
)
@invest_agent.on_rest_get("/openapi", OpenApiResponse)
async def generate_openapi_documentation(_ctx: Context):
    return cast(OpenApiResponse, spec.to_dict())


def main():
    invest_agent.run()


if __name__ == "__main__":
    main()
