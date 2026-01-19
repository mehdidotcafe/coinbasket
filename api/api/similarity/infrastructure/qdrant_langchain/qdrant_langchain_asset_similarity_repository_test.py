from unittest import mock
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from pytest import fixture, mark
from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue,
    Record,
    OrderBy,
    Direction,
)

from api.similarity.similarity_document import SimilarityDocument
from api.similarity.infrastructure.qdrant_langchain.qdrant_langchain_asset_similarity_repository import (
    QdrantLangChainAssetSimilarityRepository,
)
from qdrant_client import AsyncQdrantClient, QdrantClient
from api.protocol.fixture.token import bnb_token, eth_token, sol_token


@fixture
def qdrant_client():
    qdrant_client = mock.Mock(spec=QdrantClient)

    qdrant_client.return_value = qdrant_client

    return qdrant_client


@fixture
def qdrant_async_client():
    qdrant_async_client = mock.Mock(spec=AsyncQdrantClient)

    qdrant_async_client.return_value = qdrant_async_client

    return qdrant_async_client


@fixture
def qdrant_vector_store():
    qdrant_vector_store = mock.Mock(spec=QdrantVectorStore)

    qdrant_vector_store.return_value = qdrant_vector_store

    return qdrant_vector_store


@fixture
def embeddings():
    return mock.Mock(spec=OpenAIEmbeddings)


@fixture
def fetch_limit():
    return 100


@fixture
def return_limit():
    return 5


@mark.asyncio
async def test_qdrant_langchain_asset_similarity_repository_search_with_name_or_ticker_no_reranking(
    qdrant_client: type[QdrantClient],
    qdrant_async_client: type[AsyncQdrantClient],
    qdrant_vector_store: type[QdrantVectorStore],
    embeddings: OpenAIEmbeddings,
    fetch_limit: int,
):
    name = "coin"

    similarity_storage = QdrantLangChainAssetSimilarityRepository(
        {
            "qdrant_url": "http://localhost",
            "qdrant_port": 6333,
            "qdrant_grpc_port": 6334,
            "qdrant_collection": "datasets",
            "qdrant_api_key": "d011246a-b8dd-4a8c-baf2-7ec12f2507db",
        },
        qdrant_client,
        qdrant_async_client,
        qdrant_vector_store,
        embeddings,
    )

    similarity_storage.start()

    bnb_token_similarity = bnb_token.to_dict() | {
        "market_cap_usd": 0,
        "is_canonical": 1,
    }
    eth_token_similarity = eth_token.to_dict() | {
        "market_cap_usd": 0,
        "is_canonical": 1,
    }

    qdrant_vector_store.asimilarity_search_with_score.return_value = [
        (
            Document(
                page_content="page content 1",
                metadata={"_id": "1", "type": "token", "source": bnb_token_similarity},
            ),
            0.9,
        ),
        (
            Document(
                page_content="page content 2",
                metadata={"_id": "2", "type": "token", "source": eth_token_similarity},
            ),
            0.8,
        ),
    ]

    assets = await similarity_storage.similarity_search(name, "TOKEN")

    assert assets == [
        bnb_token,
        eth_token,
    ]

    qdrant_client.assert_called_once_with(
        url="http://localhost",
        port=6333,
        grpc_port=6334,
        api_key="d011246a-b8dd-4a8c-baf2-7ec12f2507db",
        prefer_grpc=True,
    )
    qdrant_vector_store.assert_called_once_with(
        client=qdrant_client.return_value,
        collection_name="datasets",
        embedding=embeddings,
    )
    qdrant_vector_store.asimilarity_search_with_score.assert_called_once_with(
        name,
        fetch_limit,
        filter=Filter(
            must=[
                FieldCondition(
                    key="metadata.type",
                    match=MatchValue(value="token"),
                )
            ]
        ),
    )


@mark.asyncio
async def test_qdrant_langchain_asset_similarity_repository_search_with_name_or_ticker_reranking(
    qdrant_client: type[QdrantClient],
    qdrant_async_client: type[AsyncQdrantClient],
    qdrant_vector_store: type[QdrantVectorStore],
    embeddings: OpenAIEmbeddings,
):
    name = "coin"

    similarity_storage = QdrantLangChainAssetSimilarityRepository(
        {
            "qdrant_url": "http://localhost",
            "qdrant_port": 6333,
            "qdrant_grpc_port": 6334,
            "qdrant_collection": "datasets",
            "qdrant_api_key": "d011246a-b8dd-4a8c-baf2-7ec12f2507db",
        },
        qdrant_client,
        qdrant_async_client,
        qdrant_vector_store,
        embeddings,
    )

    similarity_storage.start()

    bnb_token_similarity = bnb_token.to_dict() | {
        "market_cap_usd": 131425427,
        "is_canonical": 1,
    }
    eth_token_similarity = eth_token.to_dict() | {
        "market_cap_usd": 379722660,
        "is_canonical": 1,
    }
    sol_token_similarity = sol_token.to_dict() | {
        "market_cap_usd": 500000000,
        "is_canonical": 1,
    }

    qdrant_vector_store.asimilarity_search_with_score.return_value = [
        (
            Document(
                page_content="page content 1",
                metadata={"_id": "1", "type": "token", "source": bnb_token_similarity},
            ),
            0.53,
        ),
        (
            Document(
                page_content="page content 2",
                metadata={"_id": "2", "type": "token", "source": eth_token_similarity},
            ),
            0.42,
        ),
        (
            Document(
                page_content="page content 3",
                metadata={"_id": "3", "type": "token", "source": sol_token_similarity},
            ),
            0.10,
        ),
    ]

    assets = await similarity_storage.similarity_search(name, "TOKEN")

    assert assets == [
        eth_token,
        bnb_token,
        sol_token,
    ]


@mark.asyncio
async def test_qdrant_langchain_asset_similarity_repository_search_with_categories(
    qdrant_client: type[QdrantClient],
    qdrant_async_client: type[AsyncQdrantClient],
    qdrant_vector_store: type[QdrantVectorStore],
    embeddings: OpenAIEmbeddings,
    fetch_limit: int,
):
    categories = ["Decentralized Finance (DeFi)", "Dogechain Ecosystem"]

    similarity_storage = QdrantLangChainAssetSimilarityRepository(
        {
            "qdrant_url": "http://localhost",
            "qdrant_port": 6333,
            "qdrant_grpc_port": 6334,
            "qdrant_collection": "datasets",
            "qdrant_api_key": "d011246a-b8dd-4a8c-baf2-7ec12f2507db",
        },
        qdrant_client,
        qdrant_async_client,
        qdrant_vector_store,
        embeddings,
    )

    similarity_storage.start()

    bnb_token_similarity = bnb_token.to_dict() | {
        "market_cap_usd": 0,
        "is_canonical": 1,
    }
    eth_token_similarity = eth_token.to_dict() | {
        "market_cap_usd": 0,
        "is_canonical": 1,
    }

    qdrant_async_client.scroll.side_effect = [
        (
            [
                Record(
                    id="1",
                    payload={
                        "metadata": {
                            "_id": "1",
                            "type": "token",
                            "source": bnb_token_similarity,
                        },
                    },
                ),
            ],
            None,
        ),
        (
            [
                Record(
                    id="2",
                    payload={
                        "metadata": {
                            "_id": "2",
                            "type": "token",
                            "source": eth_token_similarity,
                        },
                    },
                ),
            ],
            None,
        ),
    ]

    assets = await similarity_storage.similarity_search(None, "TOKEN", categories)

    assert assets == [
        bnb_token,
        eth_token,
    ]

    qdrant_client.assert_called_once_with(
        url="http://localhost",
        port=6333,
        grpc_port=6334,
        api_key="d011246a-b8dd-4a8c-baf2-7ec12f2507db",
        prefer_grpc=True,
    )
    qdrant_vector_store.assert_called_once_with(
        client=qdrant_client.return_value,
        collection_name="datasets",
        embedding=embeddings,
    )
    qdrant_vector_store.asimilarity_search_with_score.assert_not_called()

    qdrant_async_client.assert_has_calls(
        [
            mock.call.scroll(
                collection_name="datasets",
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="metadata.source.categories",
                            match=MatchValue(value="Decentralized Finance (DeFi)"),
                        ),
                        FieldCondition(
                            key="metadata.source.categories",
                            match=MatchValue(value="Dogechain Ecosystem"),
                        ),
                        FieldCondition(
                            key="metadata.type",
                            match=MatchValue(value="token"),
                        ),
                        FieldCondition(
                            key="metadata.source.is_canonical",
                            match=MatchValue(value=0),
                        ),
                    ]
                ),
                order_by=OrderBy(
                    key="metadata.source.market_cap_usd",
                    direction=Direction.DESC,
                ),
                limit=fetch_limit,
            ),
            mock.call.scroll(
                collection_name="datasets",
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="metadata.source.categories",
                            match=MatchValue(value="Decentralized Finance (DeFi)"),
                        ),
                        FieldCondition(
                            key="metadata.source.categories",
                            match=MatchValue(value="Dogechain Ecosystem"),
                        ),
                        FieldCondition(
                            key="metadata.type",
                            match=MatchValue(value="token"),
                        ),
                        FieldCondition(
                            key="metadata.source.is_canonical",
                            match=MatchValue(value=1),
                        ),
                    ]
                ),
                limit=fetch_limit,
            ),
        ]
    )


@mark.asyncio
async def test_qdrant_langchain_asset_similarity_repository_search_with_address(
    qdrant_client: type[QdrantClient],
    qdrant_async_client: type[AsyncQdrantClient],
    qdrant_vector_store: type[QdrantVectorStore],
    embeddings: OpenAIEmbeddings,
    fetch_limit: int,
):
    address = "0xabc12123def4567890abc12123def4567890abc12"

    similarity_storage = QdrantLangChainAssetSimilarityRepository(
        {
            "qdrant_url": "http://localhost",
            "qdrant_port": 6333,
            "qdrant_grpc_port": 6334,
            "qdrant_collection": "datasets",
            "qdrant_api_key": "d011246a-b8dd-4a8c-baf2-7ec12f2507db",
        },
        qdrant_client,
        qdrant_async_client,
        qdrant_vector_store,
        embeddings,
    )

    similarity_storage.start()

    bnb_token_similarity = bnb_token.to_dict() | {
        "market_cap_usd": 0,
        "is_canonical": 1,
    }

    qdrant_async_client.scroll.return_value = (
        [
            Record(
                id="1",
                payload={
                    "metadata": {
                        "_id": "1",
                        "type": "token",
                        "source": bnb_token_similarity,
                    },
                },
            ),
        ],
        None,
    )

    assets = await similarity_storage.similarity_search(address, "TOKEN")

    assert assets == [
        bnb_token,
    ]

    qdrant_vector_store.asimilarity_search_with_score.assert_not_called()

    qdrant_async_client.scroll.assert_called_once_with(
        collection_name="datasets",
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="metadata.type",
                    match=MatchValue(value="token"),
                ),
                FieldCondition(
                    key="metadata.source.address",
                    match=MatchValue(value=address),
                ),
            ]
        ),
        limit=fetch_limit,
    )


@mark.asyncio
async def test_qdrant_langchain_asset_similarity_repository_get(
    qdrant_client: type[QdrantClient],
    qdrant_async_client: type[AsyncQdrantClient],
    qdrant_vector_store: type[QdrantVectorStore],
    embeddings: OpenAIEmbeddings,
):
    ids = ["1", "2"]

    similarity_storage = QdrantLangChainAssetSimilarityRepository(
        {
            "qdrant_url": "http://localhost",
            "qdrant_port": 6333,
            "qdrant_grpc_port": 6334,
            "qdrant_collection": "datasets",
            "qdrant_api_key": "d011246a-b8dd-4a8c-baf2-7ec12f2507db",
        },
        qdrant_client,
        qdrant_async_client,
        qdrant_vector_store,
        embeddings,
    )

    similarity_storage.start()

    qdrant_vector_store.aget_by_ids.return_value = [
        Document(page_content="page content 1", metadata={"_id": "1"}),
        Document(page_content="page content 2", metadata={"_id": "2"}),
    ]

    similarities = await similarity_storage.get(ids)

    assert similarities == [
        SimilarityDocument(
            page_content="page content 1", metadata={"_id": "1"}, id="1"
        ),
        SimilarityDocument(
            page_content="page content 2", metadata={"_id": "2"}, id="2"
        ),
    ]

    qdrant_vector_store.aget_by_ids.assert_called_once_with(ids)


@mark.asyncio
async def test_qdrant_langchain_asset_similarity_repository_set(
    qdrant_client: type[QdrantClient],
    qdrant_async_client: type[AsyncQdrantClient],
    qdrant_vector_store: type[QdrantVectorStore],
    embeddings: OpenAIEmbeddings,
):
    similarity_documents = [
        SimilarityDocument(page_content="page content 1", metadata={"id": "1"}, id="1"),
        SimilarityDocument(page_content="page content 2", metadata={"id": "2"}, id="2"),
    ]

    similarity_storage = QdrantLangChainAssetSimilarityRepository(
        {
            "qdrant_url": "http://localhost",
            "qdrant_port": 6333,
            "qdrant_grpc_port": 6334,
            "qdrant_collection": "datasets",
            "qdrant_api_key": "d011246a-b8dd-4a8c-baf2-7ec12f2507db",
        },
        qdrant_client,
        qdrant_async_client,
        qdrant_vector_store,
        embeddings,
    )

    similarity_storage.start()

    similarity_storage.set(similarity_documents)

    qdrant_vector_store.add_documents.assert_called_once_with(
        [
            Document(page_content="page content 1", metadata={"id": "1"}, id="1"),
            Document(page_content="page content 2", metadata={"id": "2"}, id="2"),
        ]
    )
