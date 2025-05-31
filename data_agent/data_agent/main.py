from dataclasses import asdict
import json
from typing import Any

from pydantic import SecretStr
from data_agent.ingestion.id.id_generator import IdGenerator
from data_agent.http_request.exception.invalid_agent_key import (
    InvalidAgentKey,
)
from data_agent.ingestion.data_source.infrastructure.bsc.ai_basket_data_source import (
    AiBasketDataSource,
)
from data_agent.ingestion.data_source.infrastructure.bsc.big4_basket_data_source import (
    Big4BasketDataSource,
)
from data_agent.ingestion.data_source.infrastructure.bsc.cmc_top_10_2025 import (
    CmcTop102025BasketDataSource,
)
from data_agent.ingestion.data_source.infrastructure.bsc.cryptoummah_halal_basket_data_source import (
    CryptoUmmahHalalBasketDataSource,
)
from data_agent.ingestion.data_source.infrastructure.bsc.memecoin_mania_basket_data_source import (
    MemecoinManiaBasketDataSource,
)
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from uagents import Agent, Context

from langchain_openai import OpenAIEmbeddings

from data_agent.configuration import Configuration
from data_agent.http_request.infrastructure.requests_http_request import (
    RequestsHttpRequest,
)
from data_agent.ingestion.data_source.infrastructure.bsc.coingecko_tokens_data_source import (
    CoingeckoTokenListDataSource,
)
from data_agent.ingestion.data_source.infrastructure.bsc.pancakeswap_tokens_data_source import (
    PancakeswapTokenListDataSource,
)
from data_agent.ingestion.ingest_data_use_case import IngestDataUseCase
from data_agent.similarity.get_similarities_use_case import GetSimilaritiesUseCase
from data_agent.similarity.infrastructure.qdrant_langchain.similarity_storage.qdrant_langchain_similarity_storage import (
    QdrantLangChainSimilarityStorage,
)
from protocol import SimilarityQuery, SimilarityResponse, SimilarityValidResponse

configuration = Configuration()

data_agent = Agent(
    name=configuration.agent_name,
    seed=configuration.agent_seed,
    port=configuration.agent_port,
    endpoint=f"http://localhost:{configuration.agent_port}/submit",
)

id_generator = IdGenerator()

http_request = RequestsHttpRequest[Any]()

similarity_storage = QdrantLangChainSimilarityStorage(
    {
        "qdrant_url": configuration.qdrant_url,
        "qdrant_collection": configuration.qdrant_collection,
        "qdrant_api_key": configuration.qdrant_api_key,
    },
    QdrantClient,
    QdrantVectorStore,
    OpenAIEmbeddings(
        model=configuration.embedding_provider_model,
        api_key=SecretStr(configuration.embedding_provider_api_key),
    ),
)

get_similarities_use_case = GetSimilaritiesUseCase(similarity_storage)

ingest_data_use_case = IngestDataUseCase(
    similarity_storage,
    data_sources=[
        # CoingeckoTokenListDataSource(
        #     http_request,
        #     id_generator,
        # ),
        PancakeswapTokenListDataSource(http_request, id_generator),
        Big4BasketDataSource(),
        AiBasketDataSource(),
        CmcTop102025BasketDataSource(),
        CryptoUmmahHalalBasketDataSource(),
        MemecoinManiaBasketDataSource(),
    ],
)


@data_agent.on_event("startup")
async def on_startup(ctx: Context):
    ctx.logger.info(f"{configuration.agent_name} ready, address ${ctx.agent.address}.")

    ingest_data_use_case.execute()


@data_agent.on_rest_post("/", SimilarityQuery, SimilarityResponse)
async def handle_similarity_query(
    _ctx: Context, req: SimilarityQuery
) -> SimilarityResponse:
    if req.agent_key != configuration.agent_key:
        raise InvalidAgentKey()

    print(f"Query: {req.query}")

    serialized, retrieved_docs = await get_similarities_use_case.execute(req.query)

    print(f"Serialized: {serialized}")

    return SimilarityResponse(
        data=SimilarityValidResponse(
            serialized=serialized,
            retrieved_docs=json.dumps([asdict(doc) for doc in retrieved_docs]),
            query=req.query,
        )
    )


@data_agent.on_message(model=SimilarityQuery)
async def on_similarity_query(ctx: Context, sender: str, msg: SimilarityQuery):
    if msg.agent_key != configuration.agent_key:
        await ctx.send(
            sender,
            SimilarityResponse(data=InvalidAgentKey().message),
        )
        return

    query = msg.query

    serialized, retrieved_docs = await get_similarities_use_case.execute(msg.query)

    await ctx.send(
        sender,
        SimilarityResponse(
            data=SimilarityValidResponse(
                serialized=serialized,
                retrieved_docs=json.dumps([asdict(doc) for doc in retrieved_docs]),
                query=query,
            )
        ),
    )


def main():
    data_agent.run()


if __name__ == "__main__":
    main()
