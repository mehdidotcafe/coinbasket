from unittest import mock
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from pytest import fixture, mark
from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue,
)

from api.similarity.similarity_document import SimilarityDocument
from api.similarity.infrastructure.qdrant_langchain.similarity_storage.qdrant_langchain_similarity_storage import (
    QdrantLangChainSimilarityStorage,
)
from qdrant_client import QdrantClient


@fixture
def qdrant_client():
    qdrant_client = mock.Mock(spec=QdrantClient)

    qdrant_client.return_value = qdrant_client

    return qdrant_client


@fixture
def qdrant_vector_store():
    qdrant_vector_store = mock.Mock(spec=QdrantVectorStore)

    qdrant_vector_store.return_value = qdrant_vector_store

    return qdrant_vector_store


@fixture
def embeddings():
    return mock.Mock(spec=OpenAIEmbeddings)


@mark.asyncio
async def test_qdrant_langchain_similarity_storage_search(
    qdrant_client: type[QdrantClient],
    qdrant_vector_store: type[QdrantVectorStore],
    embeddings: OpenAIEmbeddings,
):
    query = "Please create a low risk basket without stablecoins."

    similarity_storage = QdrantLangChainSimilarityStorage(
        {
            "qdrant_url": "http://localhost",
            "qdrant_port": 6333,
            "qdrant_grpc_port": 6334,
            "qdrant_collection": "datasets",
            "qdrant_api_key": "d011246a-b8dd-4a8c-baf2-7ec12f2507db",
        },
        qdrant_client,
        qdrant_vector_store,
        embeddings,
    )

    await similarity_storage.start()

    qdrant_vector_store.asimilarity_search.return_value = [
        Document(page_content="page content 1", metadata={"_id": "1"}),
        Document(page_content="page content 2", metadata={"_id": "2"}),
    ]

    similarities = await similarity_storage.similarity_search(query, {"type": "token"})

    assert similarities == [
        SimilarityDocument(
            page_content="page content 1", metadata={"_id": "1"}, id="1"
        ),
        SimilarityDocument(
            page_content="page content 2", metadata={"_id": "2"}, id="2"
        ),
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
    qdrant_vector_store.asimilarity_search.assert_called_once_with(
        query,
        10,
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
async def test_qdrant_langchain_similarity_storage_get(
    qdrant_client: type[QdrantClient],
    qdrant_vector_store: type[QdrantVectorStore],
    embeddings: OpenAIEmbeddings,
):
    ids = ["1", "2"]

    similarity_storage = QdrantLangChainSimilarityStorage(
        {
            "qdrant_url": "http://localhost",
            "qdrant_port": 6333,
            "qdrant_grpc_port": 6334,
            "qdrant_collection": "datasets",
            "qdrant_api_key": "d011246a-b8dd-4a8c-baf2-7ec12f2507db",
        },
        qdrant_client,
        qdrant_vector_store,
        embeddings,
    )

    await similarity_storage.start()

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
async def test_qdrant_langchain_similarity_storage_set(
    qdrant_client: type[QdrantClient],
    qdrant_vector_store: type[QdrantVectorStore],
    embeddings: OpenAIEmbeddings,
):
    similarity_documents = [
        SimilarityDocument(page_content="page content 1", metadata={"id": "1"}, id="1"),
        SimilarityDocument(page_content="page content 2", metadata={"id": "2"}, id="2"),
    ]

    similarity_storage = QdrantLangChainSimilarityStorage(
        {
            "qdrant_url": "http://localhost",
            "qdrant_port": 6333,
            "qdrant_grpc_port": 6334,
            "qdrant_collection": "datasets",
            "qdrant_api_key": "d011246a-b8dd-4a8c-baf2-7ec12f2507db",
        },
        qdrant_client,
        qdrant_vector_store,
        embeddings,
    )

    await similarity_storage.start()

    similarity_storage.set(similarity_documents)

    qdrant_vector_store.add_documents.assert_called_once_with(
        [
            Document(page_content="page content 1", metadata={"id": "1"}, id="1"),
            Document(page_content="page content 2", metadata={"id": "2"}, id="2"),
        ]
    )
