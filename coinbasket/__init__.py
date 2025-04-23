from uagents import Agent, Context, Model
from dotenv import dotenv_values
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

from coinbasket.basket import Basket
from coinbasket.chain.bsc_chain import BscChain
from coinbasket.investment_planner.equal_investment_planner import (
    EqualInvestmentPlanner,
)
from coinbasket.investment_planner.insufficient_balance_exception import (
    InsufficientBalanceException,
)

config = dotenv_values()

os.environ["LANGSMITH_TRACING"] = config["LANGSMITH_TRACING"]
os.environ["LANGSMITH_API_KEY"] = config["LANGSMITH_API_KEY"]

coinbasket = Agent(
    name=config["AGENT_NAME"],
    seed=config["AGENT_SEED"],
    port=config["AGENT_PORT"],
    endpoint=f"http://localhost:{config['AGENT_PORT']}/submit",
)

loader = JSONLoader(
    file_path="./data/selection.json",
    jq_schema=".",
    text_content=False,
)

docs = loader.load()

llm = init_chat_model(
    "gpt-4o-mini", model_provider="openai", api_key=config["OPENAI_API_KEY"]
)

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small", api_key=config["OPENAI_API_KEY"]
)

vector_store = InMemoryVectorStore(embeddings)

vector_store.add_documents(docs)

chain = BscChain(
    rpc_url=config["BSC_RPC_URL"],
    private_key=config["BSC_PRIVATE_KEY"],
)
investment_planner = EqualInvestmentPlanner(chain=chain)


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
def invest(basket: Basket):
    """Invest / fund / buy the basket create by the user.

    Args:
        basket: The basket to Invest / fund / buy.
    """

    try:
        investment_plan = investment_planner.make_investment_plan(basket)

        print(investment_plan)

        return "Investment success."
    except InsufficientBalanceException as e:
        return e.message


# Step 1: Generate an AIMessage that may include a tool-call to be sent.
def query_or_respond(state: MessagesState):
    """Generate tool call for retrieval or respond."""
    llm_with_tools = llm.bind_tools([retrieve, invest, get_balance])
    response = llm_with_tools.invoke(state["messages"])
    # MessagesState appends messages to state instead of overwriting
    return {"messages": [response]}


# Step 2: Execute the retrieval.
tools = ToolNode([retrieve, invest, get_balance])


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
    graph_config = {"configurable": {"thread_id": "abc123"}}
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
