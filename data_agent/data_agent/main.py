from data_agent.asset.get_asset_by_id_use_case import GetAssetByIdUseCase
from data_agent.similarity.basket.get_all_baskets_use_case import GetAllBasketsUseCase
from pydantic import SecretStr
from data_agent.ingestion.id.id_generator import IdGenerator
from data_agent.authentication.exception.invalid_agent_key import InvalidAgentKey

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
from shared.http_request.infrastructure.requests_http_request import (
    RequestsHttpRequest,
)
from data_agent.ingestion.data_source.infrastructure.bsc.pancakeswap_tokens_data_source import (
    PancakeswapTokenListDataSource,
)
from data_agent.ingestion.ingest_data_use_case import IngestDataUseCase
from data_agent.similarity.get_similar_assets_use_case import (
    GetSimilarAssetsUseCase,
)
from data_agent.similarity.infrastructure.qdrant_langchain.similarity_storage.qdrant_langchain_similarity_storage import (
    QdrantLangChainSimilarityStorage,
)
from protocol import (
    BasketResponse,
    Token,
    SimilarAssetsQuery,
    SimilarAssetsResponse,
    SimilarAssetsValidResponse,
    GetAllBasketsQuery,
    GetAllBasketsResponse,
    TokenResponse,
    GetAssetByIdQuery,
    GetAssetByIdResponse,
    GetAssetByIdValidResponse,
)

configuration = Configuration()

data_agent = Agent(
    name=configuration.agent_name,
    seed=configuration.agent_seed,
    port=configuration.agent_port,
    endpoint=f"http://localhost:{configuration.agent_port}/submit",
)

id_generator = IdGenerator()

http_request = RequestsHttpRequest()

similarity_storage = QdrantLangChainSimilarityStorage(
    {
        "qdrant_url": configuration.qdrant_url,
        "qdrant_port": configuration.qdrant_port,
        "qdrant_grpc_port": configuration.qdrant_grpc_port,
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

get_similar_assets_use_case = GetSimilarAssetsUseCase(similarity_storage)

get_all_baskets_use_case = GetAllBasketsUseCase(similarity_storage)

get_asset_by_id_use_case = GetAssetByIdUseCase(similarity_storage)

ingest_data_use_case = IngestDataUseCase(
    similarity_storage,
    data_sources=[
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

    await ingest_data_use_case.execute()


@data_agent.on_rest_post("/", SimilarAssetsQuery, SimilarAssetsResponse)
async def get_similar_assets(
    _ctx: Context, req: SimilarAssetsQuery
) -> SimilarAssetsResponse:
    if req.agent_key != configuration.agent_key:
        raise InvalidAgentKey()

    assets = await get_similar_assets_use_case.execute(req.query, req.type)

    return SimilarAssetsResponse(
        data=SimilarAssetsValidResponse(
            assets=[
                TokenResponse.from_domain(asset)
                if isinstance(asset, Token)
                else BasketResponse.from_domain(asset)
                for asset in assets
            ],
            query=req.query,
        )
    )


@data_agent.on_message(model=SimilarAssetsQuery)
async def on_get_similar_assets_message(
    ctx: Context, sender: str, msg: SimilarAssetsQuery
):
    if msg.agent_key != configuration.agent_key:
        await ctx.send(
            sender,
            SimilarAssetsResponse(data=InvalidAgentKey().message),
        )
        return

    query = msg.query

    assets = await get_similar_assets_use_case.execute(query, type=None)

    await ctx.send(
        sender,
        SimilarAssetsResponse(
            data=SimilarAssetsValidResponse(
                assets=[
                    TokenResponse.from_domain(asset)
                    if isinstance(asset, Token)
                    else BasketResponse.from_domain(asset)
                    for asset in assets
                ],
                query=query,
            )
        ),
    )


@data_agent.on_rest_post("/basket", GetAllBasketsQuery, GetAllBasketsResponse)
async def get_all_baskets(
    _ctx: Context, req: GetAllBasketsQuery
) -> GetAllBasketsResponse:
    if req.agent_key != configuration.agent_key:
        raise InvalidAgentKey()

    baskets = await get_all_baskets_use_case.execute()

    return GetAllBasketsResponse(
        baskets=[BasketResponse.from_domain(basket) for basket in baskets]
    )


@data_agent.on_rest_post("/asset", GetAssetByIdQuery, GetAssetByIdResponse)
async def get_asset_by_id(
    _ctx: Context, req: GetAssetByIdQuery
) -> GetAssetByIdResponse:
    if req.agent_key != configuration.agent_key:
        raise InvalidAgentKey()

    asset_id = req.asset_id
    asset = await get_asset_by_id_use_case.execute(asset_id)

    if not asset:
        raise ValueError(f"Asset id {asset_id} not found")

    return GetAssetByIdResponse(
        data=GetAssetByIdValidResponse(
            asset=TokenResponse.from_domain(asset)
            if isinstance(asset, Token)
            else BasketResponse.from_domain(asset)
        )
    )


def main():
    data_agent.run()


if __name__ == "__main__":
    main()
