import time
from typing import Any
from uagents import Agent, Context, Model
from uagents.storage import KeyValueStore

import os
import sqlite3

from typing_extensions import List, TypedDict

from langchain_community.document_loaders import JSONLoader
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langchain_core.vectorstores import InMemoryVectorStore
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent

from langchain_openai import OpenAIEmbeddings
from langgraph.checkpoint.sqlite import SqliteSaver


from web3 import Web3

from invest_agent.basket import Basket, Token
from invest_agent.infrastructure.bsc.chain.bsc_chain import BscChain
from invest_agent.config import Config
from invest_agent.investment.basket_divest_use_case import BasketDivestUseCase
from invest_agent.investment.divestment_planner_strategy.total_divestment_planner import (
    TotalDivestmentPlanner,
)
from invest_agent.investment.get_investment_result_use_case import (
    GetInvestmentResultUseCase,
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

thread_id = str(int(time.time()))

print(f"Thread ID: {thread_id}")

config = Config()

os.environ["LANGSMITH_TRACING"] = config.langsmith_tracing
os.environ["LANGSMITH_API_KEY"] = config.langsmith_api_key

invest_agent = Agent(
    name=config.agent_name,
    seed=config.agent_seed,
    port=config.agent_port,
    endpoint=f"http://localhost:{config.agent_port}/submit",
)

loader = JSONLoader(
    file_path="./data/selection.json",
    jq_schema=".",
    text_content=False,
)

docs = loader.load()

llm = init_chat_model(
    "gpt-4o-mini", model_provider="openai", api_key=config.openai_api_key
)

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small", api_key=config.openai_api_key
)

vector_store = InMemoryVectorStore(embeddings)

vector_store.add_documents(docs)

chain = BscChain(
    w3=Web3(Web3.HTTPProvider(config.bsc_rpc_url)),
    private_key=config.bsc_private_key,
    base_token=Token(
        name=config.bsc_base_token_name,
        display_name=config.bsc_base_token_display_name,
        ticker=config.bsc_base_token_ticker,
        address=config.bsc_base_token_address,
    ),
)
permit2 = Permit2(
    chain=chain,
    permit2_contract_address=config.pancakeswap_permit2_contract_address,
    bsc_rpc_url=config.bsc_rpc_url,
    private_key=config.bsc_private_key,
)
exchange = PancakeSwapUniversalRouter(
    config.bsc_rpc_url,
    config.pancakeswap_universal_router_address,
    config.pancakeswap_v2_router_address,
    config.bsc_private_key,
    chain,
    permit2,
)
storage = FetchAiStorage[Any](
    thread_id, store=KeyValueStore(config.agent_name, "./database")
)

basket_invest_use_case = BasketInvestUseCase(
    investment_planner=EqualInvestmentPlanner(chain),
    exchange=exchange,
    storage=storage,
)
basket_divest_use_case = BasketDivestUseCase(
    divestment_planner=TotalDivestmentPlanner(chain),
    exchange=exchange,
    storage=storage,
)
get_invested_basket_use_case = GetInvestmentResultUseCase(storage=storage)


class State(TypedDict):
    question: str
    context: List[Document]
    answer: str


@tool(response_format="content_and_artifact")
def retrieve(query: str):
    """
    Retrieve a list of available coins to invest.

    Args:
        query: The query to search for.

    Returns:
        A list of documents containing the available coins to make the basket with.
        Each coin has a name, display_name, ticker and address (contract address) property.
    """
    retrieved_docs = vector_store.similarity_search(query)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs


@tool()
def get_balance():
    """Retrieve agent's current wallet balance."""
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
    """
    return basket_invest_use_case.execute(basket)


@tool()
def divest_basket():
    """Divest / sell the basket create by the user.

    Args:
        basket: The basket to Invest / fund / buy.
    """
    return basket_divest_use_case.execute()


sqliteMemory = SqliteSaver(
    sqlite3.connect("./database/langchain_graphs.db", check_same_thread=False)
)

agent_executor = create_react_agent(
    llm,
    [retrieve, invest_basket, get_balance, get_invested_basket, divest_basket],
    checkpointer=sqliteMemory,
    prompt=SystemMessage(
        "Your goal is to create and then invest in crypto coin baskets.  "
        "Always give a name to the basket you are creating. Reevaluate the basket name after each answer.  "
        "Always show the user the basket you are creating by showing its name and listing the coins in a single list with the coin display name, ticker and address. Don't mention excluded coins.  "
        "After each answer, ask the user if he wants to add or remove any coins from the basket or if he wants to invest in the basket.  "
        "Always ask for the user's confirmation before investing in the basket.  "
        "When you display a token, always show its address.  "
        "If you don't know the answer, just say that you don't know, don't try to make up an answer.  "
    ),
)


class PromptRequest(Model):
    text: str


class PromptResponse(Model):
    text: str


@invest_agent.on_rest_post("/", PromptRequest, PromptResponse)
async def handle_post(ctx: Context, req: PromptRequest) -> PromptResponse:
    graph_config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }
    question = req.text

    for step in agent_executor.stream(
        {"messages": [{"role": "user", "content": question}]},
        stream_mode="values",
        config=graph_config,
    ):
        step["messages"][-1].pretty_print()

    ctx.logger.info(f"Received request with text: {req.text}")

    return PromptResponse(text=step["messages"][-1].content)


def main():
    invest_agent.run()


if __name__ == "__main__":
    main()
