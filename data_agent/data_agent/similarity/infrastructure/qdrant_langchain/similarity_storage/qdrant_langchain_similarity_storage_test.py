from unittest import mock
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from pytest import fixture

from data_agent.similarity.similarity_document import SimilarityDocument
from data_agent.similarity.infrastructure.qdrant_langchain.similarity_storage.qdrant_langchain_similarity_storage import (
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


def test_qdrant_langchain_similarity_storage_search(
    qdrant_client: type[QdrantClient],
    qdrant_vector_store: type[QdrantVectorStore],
    embeddings: OpenAIEmbeddings,
):
    query = "Please create a low risk basket without stablecoins."

    similarity_storage = QdrantLangChainSimilarityStorage(
        {
            "qdrant_url": "http://localhost:6333",
            "qdrant_collection": "datasets",
            "qdrant_api_key": "d011246a-b8dd-4a8c-baf2-7ec12f2507db",
        },
        qdrant_client,
        qdrant_vector_store,
        embeddings,
    )

    qdrant_vector_store.similarity_search.return_value = [
        Document(page_content="page content 1", metadata={"id": "1"}),
        Document(page_content="page content 2"),
    ]

    similarities = similarity_storage.similarity_search(query)

    assert similarities == [
        SimilarityDocument(page_content="page content 1", metadata={"id": "1"}),
        SimilarityDocument(page_content="page content 2", metadata=None),
    ]

    qdrant_client.assert_called_once_with(
        url="http://localhost:6333",
        api_key="d011246a-b8dd-4a8c-baf2-7ec12f2507db",
        prefer_grpc=True,
    )
    qdrant_vector_store.assert_called_once_with(
        client=qdrant_client.return_value,
        collection_name="datasets",
        embedding=embeddings,
    )
    qdrant_vector_store.similarity_search.assert_called_once_with(query)


def test_qdrant_langchain_similarity_storage_set(
    qdrant_client: type[QdrantClient],
    qdrant_vector_store: type[QdrantVectorStore],
    embeddings: OpenAIEmbeddings,
):
    similarity_documents = [
        SimilarityDocument(page_content="page content 1", metadata={"id": "1"}),
        SimilarityDocument(page_content="page content 2", metadata=None),
    ]

    similarity_storage = QdrantLangChainSimilarityStorage(
        {
            "qdrant_url": "http://localhost:6333",
            "qdrant_collection": "datasets",
            "qdrant_api_key": "d011246a-b8dd-4a8c-baf2-7ec12f2507db",
        },
        qdrant_client,
        qdrant_vector_store,
        embeddings,
    )

    similarity_storage.set(similarity_documents)

    qdrant_vector_store.add_documents.assert_called_once_with(
        [
            Document(page_content="page content 1", metadata={"id": "1"}),
            Document(page_content="page content 2", metadata=dict()),
        ]
    )
