from uagents import Agent, Context

from langchain_community.document_loaders import JSONLoader
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings

from jsonpickle import encode

from data_agent.configuration import Configuration
from protocol.protocol import SimilarityQuery, SimilarityResponse

configuration = Configuration()

data_agent = Agent(
    name=configuration.agent_name,
    seed=configuration.agent_seed,
    port=configuration.agent_port,
    endpoint=f"http://localhost:{configuration.agent_port}/submit",
)


loader = JSONLoader(
    file_path="./data/selection.json",
    jq_schema=".",
    text_content=False,
)

docs = loader.load()

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small", api_key=configuration.openai_api_key
)

vector_store = InMemoryVectorStore(embeddings)

vector_store.add_documents(docs)


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


@data_agent.on_event("startup")
async def on_startup(ctx: Context):
    ctx.logger.info(f"{configuration.agent_name} ready, address ${ctx.agent.address}.")


@data_agent.on_message(model=SimilarityQuery)
async def on_similarity_query(ctx: Context, sender: str, msg: SimilarityQuery):
    ctx.logger.info(f"I have received a message from {sender}.")

    serialized, retrieved_docs = retrieve(msg.query)

    encoded_docs: str | None = encode(retrieved_docs)

    print(f"Encoded docs: {encoded_docs}")

    if not encoded_docs:
        raise ValueError("Encoded documents are None.")

    await ctx.send(
        sender,
        SimilarityResponse(
            serialized=serialized,
            retrieved_docs=encoded_docs,
        ),
    )


def main():
    data_agent.run()


if __name__ == "__main__":
    main()
