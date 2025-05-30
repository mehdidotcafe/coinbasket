import os
from typing import Any, Dict, Optional, cast

import aiohttp
from invest_agent.authentication.authentication import authentication
from invest_agent.conversation.get_conversation_messages_use_case import (
    GetConversationMessagesUseCase,
)
from invest_agent.conversation.repository.infrastructure.langchain_sqlite_conversation_repository import (
    LangchainSqliteConversationRepository,
)
from invest_agent.datetime.infrastructure.python_date_time import PythonDateTime
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
from protocol.basket import Basket
from protocol.token import Token
from uagents import Agent, Context, Model
from uagents.storage import KeyValueStore

import aiosqlite

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from web3 import Web3

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

date_time = PythonDateTime()

thread_id = str(date_time.now())
# thread_id = "1748622992"

print(f"Thread ID: {thread_id}")

configuration = Configuration()

os.environ["LANGSMITH_TRACING"] = configuration.langsmith_tracing
os.environ["LANGSMITH_API_KEY"] = configuration.langsmith_api_key

invest_agent = Agent(
    name=configuration.agent_name,
    seed=configuration.agent_seed,
    port=configuration.agent_port,
    endpoint=f"http://localhost:{configuration.agent_port}/submit",
)

w3 = Web3(Web3.HTTPProvider(configuration.bsc_rpc_url))

chain = BscChain(
    w3=w3,
    private_key=configuration.bsc_private_key,
    base_token=Token(
        name=configuration.bsc_base_token_name,
        display_name=configuration.bsc_base_token_display_name,
        ticker=configuration.bsc_base_token_ticker,
        address=configuration.bsc_base_token_address,
    ),
)

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
    thread_id, store=KeyValueStore(configuration.agent_name, "./database")
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
)
get_invested_basket_use_case = GetBasketInvestmentUseCase(storage=storage)

get_basket_balance_in_token_use_case = GetWalletInTokenUseCase(
    storage=storage, exchange=exchange, chain=chain
)


conversation_repository = LangchainSqliteConversationRepository(
    db_path="./database/langchain_graphs.db", date_time=date_time
)

get_conversation_messages_use_case = GetConversationMessagesUseCase(
    conversation_repository=conversation_repository
)


@tool(response_format="content_and_artifact")
async def get_available_basket_or_coin_info(query: str):
    """
    Retrieve a list of available tokens / coins to invest.
    Retrieve a list of available baskets to invest.

    Args:
        query: The query to search for.

    Returns:
        A list of documents containing tokens or a basket.
        Each token has a name, display_name, ticker and address (contract address) property.
        A basket is made of a name, a description and a list of tokens.
    """
    # TODO: Use fetch ai send_and_receive when fixed with multiple concurrent requests
    res = await agent_to_agent_client.send_and_receive_message(
        SimilarityQuery(query=query, agent_key=configuration.data_agent_key),
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
def get_balance():
    """Retrieve agent's current wallet balance in BNB."""
    return chain.get_balance()


@tool()
def get_invested_basket():
    """Retrieve the invested basket.

    Returns:
        The invested basket made of the bids that were made by the agent when investing in the basket.
        Each bid has a token and a balance_in and balance_out property.
        The token has a name, display_name, ticker and address (contract address) property.
    """
    return get_invested_basket_use_case.execute()


@tool(response_format="content_and_artifact")
def invest_basket(basket: Basket):
    """Invest / fund / buy the basket create by the user.
    Each basket coin needs to have a name, ticker and address.

    Args:
        basket: The basket to Invest / fund / buy.

    Returns:
        BasketInvestment: The basket investment made of the bids that were made by the agent when investing in the basket.
    """
    message, basket_investment = basket_invest_use_case.execute(basket)

    if basket_investment is None:
        return message, None

    content: Dict[str, str | BasketInvestment] = {
        "message": message,
        "basket_investment": basket_investment,
    }

    return content, basket_investment


@tool()
def divest_basket():
    """Divest / sell the basket create by the user.

    Args:
        basket: The basket to Invest / fund / buy.
    """
    return basket_divest_use_case.execute()


llm = init_chat_model(
    "gpt-4o-mini", model_provider="openai", api_key=configuration.openai_api_key
)


def create_agent_executor(conn: aiosqlite.Connection):
    sqliteMemory = AsyncSqliteSaver(conn)

    agent_executor = create_react_agent(
        llm,
        [
            get_available_basket_or_coin_info,
            invest_basket,
            get_address,
            get_balance,
            get_invested_basket,
            divest_basket,
        ],
        checkpointer=sqliteMemory,
        prompt=SystemMessage(
            f"Your name is {configuration.agent_name}.  "
            "Your goal is to create and then invest in crypto coin baskets on binance smart chain.  "
            f"Today is {date_time.now_str()}.  "
            "Always give a name to the basket you are creating. Reevaluate the basket name after each answer.  "
            "Always show the user the basket you are creating by showing its name and listing the coins in a single list with the coin display name, ticker and address. Don't mention excluded coins.  "
            "When you display a token, always show its address as a link using this link 'https://bscscan.com/token/[token_address]'.  "
            "After each answer, ask the user if he wants to add or remove any coins from the basket or if he wants to invest in the basket.  "
            "Always ask for the user's confirmation before investing in the basket and show a message mentioning that he should do his own research (DYOR) before investing.  "
            "Always ask for the user's confirmation before divesting the basket. "
            "Always use get_basket_or_coin_info to retrieve the list of available tokens / coins to invest.  "
            # "You can manage / invest in only one basket at a time.  "
            # "You can update a created basket but once it has been invested, you can only divest it and you can't update it anymore.  "
            # "You can't create a basket if you already have one.  "
            "If you don't know the answer, just say that you don't know, don't try to make up an answer.  "
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


@invest_agent.on_rest_post("/conversation", PromptRequest, MessageResponse)
@authentication(configuration.agent_key)
async def conversation(_ctx: Context, req: PromptRequest) -> MessageResponse:
    async with aiosqlite.connect("./database/langchain_graphs.db") as conn:
        agent_executor = create_agent_executor(conn)

        graph_config: RunnableConfig = {
            "configurable": {
                "thread_id": thread_id,
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


@invest_agent.on_rest_post("/conversation/messages", MessagesRequest, MessagesResponse)
@authentication(configuration.agent_key)
async def get_conversation_messages(
    _ctx: Context,
    _req: MessagesRequest,
) -> MessagesResponse:
    """Retrieve the conversation messages."""
    messages = await get_conversation_messages_use_case.execute(thread_id=thread_id)

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


@invest_agent.on_rest_post("/auth", AuthRequest, AuthResponse)
@authentication(configuration.agent_key)
async def auth_request(_ctx: Context, _req: AuthRequest) -> AuthResponse:
    return AuthResponse(status="OK")


class HealthResponse(Model):
    status: str


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
    balance: str
    token: TokenResponse


class ConvertedBalanceResponse(Model):
    balance_in: BalanceResponse
    balance_out: BalanceResponse


class MetricsWalletRequest(Model):
    agent_key: str
    token: TokenRequest


class MetricsWalletResponse(Model):
    balances: list[ConvertedBalanceResponse]
    total_balance: BalanceResponse


@invest_agent.on_rest_post(
    "/metrics/wallet/token",
    MetricsWalletRequest,
    MetricsWalletResponse,
)
@authentication(configuration.agent_key)
async def get_wallet_in_token(_ctx: Context, req: MetricsWalletRequest):
    converted_token_balances = get_basket_balance_in_token_use_case.execute(
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
                balance_in=BalanceResponse(
                    balance=str(balance.balance_in.amount),
                    token=TokenResponse(
                        name=balance.balance_in.token.name,
                        display_name=balance.balance_in.token.display_name,
                        ticker=balance.balance_in.token.ticker,
                        address=balance.balance_in.token.address,
                    ),
                ),
                balance_out=BalanceResponse(
                    balance=str(balance.balance_out.amount),
                    token=TokenResponse(
                        name=balance.balance_out.token.name,
                        display_name=balance.balance_out.token.display_name,
                        ticker=balance.balance_out.token.ticker,
                        address=balance.balance_out.token.address,
                    ),
                ),
            )
            for balance in converted_token_balances.balances
        ],
        total_balance=BalanceResponse(
            balance=str(converted_token_balances.total_balance.amount),
            token=TokenResponse(
                name=converted_token_balances.total_balance.token.name,
                display_name=converted_token_balances.total_balance.token.display_name,
                ticker=converted_token_balances.total_balance.token.ticker,
                address=converted_token_balances.total_balance.token.address,
            ),
        ),
    )


def main():
    invest_agent.run()


if __name__ == "__main__":
    main()
