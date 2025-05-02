from typing import Any
from uagents import Agent, Context, Model
from uagents.storage import KeyValueStore

import os

from typing_extensions import List, TypedDict

from langchain_community.document_loaders import JSONLoader

from langgraph.checkpoint.memory import MemorySaver

from langchain_core.documents import Document
from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langchain_core.vectorstores import InMemoryVectorStore


from langchain.chat_models import init_chat_model

from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph, MessagesState, END

from langchain_openai import OpenAIEmbeddings
from web3 import Web3

from coinbasket.basket import Basket, Token
from coinbasket.infrastructure.bsc.chain.bsc_chain import BscChain
from coinbasket.config import Config
from coinbasket.investment.basket_divest_use_case import BasketDivestUseCase
from coinbasket.investment.divestment_planner_strategy.total_divestment_planner import (
    TotalDivestmentPlanner,
)
from coinbasket.investment.get_investment_result_use_case import (
    GetInvestmentResultUseCase,
)
from coinbasket.investment.infrastructure.pancakeswap.exchange.permit2 import Permit2
from coinbasket.investment.invest_use_case import InvestUseCase
from coinbasket.investment.investment_planner_strategy.equal_investment_planner import (
    EqualInvestmentPlanner,
)
from coinbasket.investment.infrastructure.pancakeswap.exchange.universal_router import (
    PancakeSwapUniversalRouter,
)
from coinbasket.infrastructure.fetch_ai.storage.fetch_ai_storage import (
    FetchAiStorage,
)

config = Config()

os.environ["LANGSMITH_TRACING"] = config.langsmith_tracing
os.environ["LANGSMITH_API_KEY"] = config.langsmith_api_key

coinbasket = Agent(
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
storage = FetchAiStorage[Any](store=KeyValueStore(config.agent_name))

invest_use_case = InvestUseCase(
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
    """Retrieve information related to a query."""
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
    """Retrieve the invested basket."""
    return get_invested_basket_use_case.execute()


@tool(response_format="content_and_artifact")
def invest_basket(basket: Basket):
    """Invest / fund / buy the basket create by the user.

    Args:
        basket: The basket to Invest / fund / buy.
    """
    return invest_use_case.execute(basket)


@tool()
def divest_basket():
    """Divest / sell the basket create by the user.

    Args:
        basket: The basket to Invest / fund / buy.
    """
    return basket_divest_use_case.execute()


# Step 1: Generate an AIMessage that may include a tool-call to be sent.
def query_or_respond(state: MessagesState):
    """Generate tool call for retrieval or respond."""
    llm_with_tools = llm.bind_tools(
        [retrieve, invest_basket, get_balance, get_invested_basket, divest_basket]
    )
    response = llm_with_tools.invoke(state["messages"])
    # MessagesState appends messages to state instead of overwriting
    return {"messages": [response]}


# Step 2: Execute the retrieval.
tools = ToolNode(
    [retrieve, invest_basket, get_balance, get_invested_basket, divest_basket]
)


# Step 3: Generate a response using the retrieved content.
def generate(state: MessagesState):
    """Generate answer."""
    # Get generated ToolMessages
    recent_tool_messages = []
    for message in reversed(state["messages"]):
        if message.type == "tool":
            recent_tool_messages.append(message)
        else:
            break
    tool_messages = recent_tool_messages[::-1]

    # Format into prompt
    docs_content = "\n\n".join(doc.content for doc in tool_messages)
    system_message_content = (
        "Your goal is to create and then invest in crypto coin baskets.  "
        "Always give a name to the basket you are creating. Reevaluate the basket name after each answer.  "
        "Always show the user the basket you are creating by showing its name and listing the coins in a single list with the coin display name and the coin ticker between parenthesis. Don't mention excluded coins.  "
        "After each answer, ask the user if he wants to add or remove any coins from the basket or if he wants to invest in the basket.  "
        "If you don't know the answer, just say that you don't know, don't try to make up an answer.  "
        "Use the following pieces of context to answer the question at the end.  "
        "Context: "
        f"{docs_content}"
    )
    conversation_messages = [
        message
        for message in state["messages"]
        if message.type in ("human", "system")
        or (message.type == "ai" and not message.tool_calls)
    ]
    prompt = [SystemMessage(system_message_content)] + conversation_messages

    # Run
    response = llm.invoke(prompt)
    return {"messages": [response]}


# Build graph
graph_builder = StateGraph(MessagesState)

graph_builder.add_node(query_or_respond)
graph_builder.add_node(tools)
graph_builder.add_node(generate)

graph_builder.set_entry_point("query_or_respond")
graph_builder.add_conditional_edges(
    "query_or_respond",
    tools_condition,
    {END: END, "tools": "tools"},
)
graph_builder.add_edge("tools", "generate")
graph_builder.add_edge("generate", END)

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)


class PromptRequest(Model):
    text: str


class PromptResponse(Model):
    text: str


@coinbasket.on_rest_post("/", PromptRequest, PromptResponse)
async def handle_post(ctx: Context, req: PromptRequest) -> PromptResponse:
    graph_config = {"configurable": {"thread_id": "abc123", "storage": ctx.storage}}
    question = req.text

    for step in graph.stream(
        {"messages": [{"role": "user", "content": question}]},
        stream_mode="values",
        config=graph_config,
    ):
        step["messages"][-1].pretty_print()

    ctx.logger.info(f"Received request with text: {req.text}")

    return PromptResponse(text=step["messages"][-1].content)


def main():
    coinbasket.run()


if __name__ == "__main__":
    main()
