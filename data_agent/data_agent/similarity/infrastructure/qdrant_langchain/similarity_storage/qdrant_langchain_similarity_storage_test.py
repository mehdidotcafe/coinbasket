from unittest import mock
from langchain_community.vectorstores import Qdrant
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import JSONLoader
from langchain_core.documents import Document
from pytest import fixture

from data_agent.similarity.similarity_document import SimilarityDocument
from data_agent.similarity.infrastructure.qdrant_langchain.similarity_storage.qdrant_langchain_similarity_storage import (
    QdrantLangChainSimilarityStorage,
)


@fixture
def qdrant():
    qdrant = mock.Mock(spec=Qdrant)

    qdrant.from_documents.return_value = qdrant

    return qdrant


@fixture
def embeddings():
    return mock.Mock(spec=OpenAIEmbeddings)


def test_qdrant_langchain_similarity_storage(
    qdrant: type[Qdrant], embeddings: OpenAIEmbeddings
):
    query = "Please create a low risk basket without stablecoins."

    similarity_storage = QdrantLangChainSimilarityStorage(
        {
            "qdrant_url": "http://localhost:6333",
            "qdrant_api_key": "d011246a-b8dd-4a8c-baf2-7ec12f2507db",
        },
        qdrant,
        embeddings,
    )

    qdrant.similarity_search.return_value = [
        Document(page_content="page content 1", metadata={"id": "1"}),
        Document(page_content="page content 2"),
    ]

    similarities = similarity_storage.similarity_search(query)

    assert similarities == [
        SimilarityDocument(page_content="page content 1", metadata={"id": "1"}),
        SimilarityDocument(page_content="page content 2", metadata=None),
    ]

    qdrant.from_documents.assert_called_once_with(
        JSONLoader(
            file_path="./data/selection.json",
            jq_schema=".",
            text_content=False,
        ).load(),
        embeddings,
        url="http://localhost:6333",
        prefer_grpc=True,
        api_key="d011246a-b8dd-4a8c-baf2-7ec12f2507db",
        collection_name="dataset",
        force_recreate=True,
    )
    qdrant.similarity_search.assert_called_once_with(query)
