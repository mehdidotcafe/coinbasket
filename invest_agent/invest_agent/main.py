import json
import os
from typing import Any, Dict
from invest_agent.datetime.infrastructure.python_date_time import PythonDateTime
from invest_agent.http.exception.invalid_authentication_exception import (
    InvalidAuthenticationException,
)
from invest_agent.investment.basket_investment import BasketInvestment
from protocol.basket import Basket
from protocol.token import Token
from uagents import Agent, Context, Model
from uagents.storage import KeyValueStore

import aiosqlite

from langchain_core.messages import SystemMessage
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
from invest_agent.investment.infrastructure.pancakeswap.exchange.permit2 import Permit2
from invest_agent.investment.basket_invest_use_case import BasketInvestUseCase
from invest_agent.investment.investment_planner_strategy.equal_investment_planner import (
    EqualInvestmentPlanner,
)
from invest_agent.investment.infrastructure.pancakeswap.exchange.universal_router import (
    PancakeSwapUniversalRouter,
)
from invest_agent.infrastructure.fetch_ai.storage.fetch_ai_storage import (
    FetchAiStorage,
)

from protocol import SimilarityQuery, SimilarityResponse

date_time = PythonDateTime()

thread_id = str(date_time.now())

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

chain = BscChain(
    w3=Web3(Web3.HTTPProvider(configuration.bsc_rpc_url)),
    private_key=configuration.bsc_private_key,
    base_token=Token(
        name=configuration.bsc_base_token_name,
        display_name=configuration.bsc_base_token_display_name,
        ticker=configuration.bsc_base_token_ticker,
        address=configuration.bsc_base_token_address,
    ),
)
permit2 = Permit2(
    chain=chain,
    permit2_contract_address=configuration.pancakeswap_permit2_contract_address,
    bsc_rpc_url=configuration.bsc_rpc_url,
    private_key=configuration.bsc_private_key,
)
exchange = PancakeSwapUniversalRouter(
    configuration.bsc_rpc_url,
    configuration.pancakeswap_universal_router_address,
    configuration.pancakeswap_v2_router_address,
    configuration.bsc_private_key,
    chain,
    permit2,
)
storage = FetchAiStorage[Any](
    thread_id, store=KeyValueStore(configuration.agent_name, "./database")
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


@tool(response_format="content_and_artifact")
async def retrieve(query: str, runnableConfig: RunnableConfig):
    """
    Retrieve a list of available tokens to invest.
    Retrieve a list of available baskets to invest.

    Args:
        query: The query to search for.

    Returns:
        A list of documents containing tokens or a basket.
        Each token has a name, display_name, ticker and address (contract address) property.
        A basket is made of a name, a description and a list of tokens.
    """
    ctx: Context | None = runnableConfig.get("configurable", {}).get("ctx")

    if ctx is None:
        raise ValueError("Context is not available in the config.")

    res, _status = await ctx.send_and_receive(
        configuration.data_agent_address,
        SimilarityQuery(query=query, agent_key=configuration.data_agent_key),
        SimilarityResponse,
    )

    if not isinstance(res, SimilarityResponse):
        raise ValueError("Response is None.")

    if isinstance(res.data, str):
        raise ValueError(f"Response is not a valid response: {res.data}")

    retrieved_docs = json.loads(res.data.retrieved_docs)

    serialized = res.data.serialized

    return serialized, retrieved_docs


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
    conn = aiosqlite.connect("./database/langchain_graphs.db", check_same_thread=False)
    sqliteMemory = AsyncSqliteSaver(conn)

    agent_executor = create_react_agent(
        llm,
        [
            retrieve,
            invest_basket,
            get_address,
            get_balance,
            get_invested_basket,
            divest_basket,
        ],
        checkpointer=sqliteMemory,
        prompt=SystemMessage(
            "Your goal is to create and then invest in crypto coin baskets on binance smart chain.  "
            f"Today is {date_time.now_str()}.  "
            "Always give a name to the basket you are creating. Reevaluate the basket name after each answer.  "
            "Always show the user the basket you are creating by showing its name and listing the coins in a single list with the coin display name, ticker and address. Don't mention excluded coins.  "
            "When you display a token, always show its address as a link using this link 'https://bscscan.com/token/[token_address]'.  "
            "After each answer, ask the user if he wants to add or remove any coins from the basket or if he wants to invest in the basket.  "
            "Always ask for the user's confirmation before investing in the basket and show a message mentioning that he should do his own research (DYOR) before investing.  "
            "Always ask for the user's confirmation before divesting the basket. "
            "You can manage / invest in only one basket at a time.  "
            "You can update a created basket but once it has been invested, you can only divest it and you can't update it anymore.  "
            "You can't create a basket if you already have one.  "
            "If you don't know the answer, just say that you don't know, don't try to make up an answer.  "
        ),
    )

    return agent_executor


class AuthRequest(Model):
    agent_key: str


class AuthResponse(Model):
    status: str


@invest_agent.on_rest_post("/auth", AuthRequest, AuthResponse)
async def auth_request(ctx: Context, req: AuthRequest) -> AuthResponse:
    if req.agent_key != configuration.agent_key:
        raise InvalidAuthenticationException()
    return AuthResponse(status="OK")


class HealthResponse(Model):
    status: str


@invest_agent.on_rest_get("/health", HealthResponse)
async def health_check(_ctx: Context) -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="OK")


class PromptRequest(Model):
    content: str
    agent_key: str


class PromptResponse(Model):
    content: str


@invest_agent.on_rest_post("/conversation", PromptRequest, PromptResponse)
async def conversation(ctx: Context, req: PromptRequest) -> PromptResponse:
    if req.agent_key != configuration.agent_key:
        raise InvalidAuthenticationException()

    async with aiosqlite.connect(
        "./database/langchain_graphs.db", check_same_thread=False
    ) as conn:
        agent_executor = create_agent_executor(conn)

        graph_config: RunnableConfig = {
            "configurable": {
                "thread_id": thread_id,
                "ctx": ctx,
            }
        }
        question = req.content

        async for step in agent_executor.astream(
            {"messages": [{"role": "user", "content": question}]},
            stream_mode="values",
            config=graph_config,
        ):
            step["messages"][-1].pretty_print()

        last_message = step["messages"][-1]

        ctx.logger.info(f"Received request with content: {req.content}")

        return PromptResponse(content=last_message.content)


def main():
    invest_agent.run()


if __name__ == "__main__":
    main()
