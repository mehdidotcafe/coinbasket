from uagents import Agent, Context, Model
from dotenv import dotenv_values
import os

from typing_extensions import List, TypedDict

from langchain_community.llms import OpenAI
from langchain_community.document_loaders import JSONLoader

from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.vectorstores import InMemoryVectorStore

from langgraph.graph import START, StateGraph

from langchain_openai import OpenAIEmbeddings

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

llm = OpenAI(
    api_key=config["OPENAI_API_KEY"],
    model="gpt-4.1-nano",
)

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small", api_key=config["OPENAI_API_KEY"]
)

vector_store = InMemoryVectorStore(embeddings)

vector_store.add_documents(docs)

template = """Your goal is to create crypto baskets.
Always show the user the basket you are creating by listing the coins in a single list with the coin display name and the ticker between parenthesis. Don't mention excluded coins.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Use the following pieces of context to answer the question at the end.

Context: {context}
Question: {question}"""
prompt = PromptTemplate.from_template(template)


class State(TypedDict):
    question: str
    context: List[Document]
    answer: str


def retrieve(state: State):
    retrieved_docs = vector_store.similarity_search(state["question"])
    return {"context": retrieved_docs}


def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})

    response = llm.invoke(messages)

    print(response)

    return {"answer": response}


graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()


class PromptRequest(Model):
    text: str


class PromptResponse(Model):
    text: str


@coinbasket.on_rest_post("/", PromptRequest, PromptResponse)
async def handle_post(ctx: Context, req: PromptRequest) -> PromptResponse:
    response = graph.invoke(
        {
            "question": req.text,
        }
    )

    ctx.logger.info(f"Received request with text: {req.text}")
    print(response)

    return PromptResponse(text=response["answer"])


def main():
    coinbasket.run()


if __name__ == "__main__":
    main()
