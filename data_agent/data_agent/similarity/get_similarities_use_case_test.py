from unittest import mock
from pytest import fixture
from data_agent.similarity.similarity_document import SimilarityDocument
from data_agent.similarity.get_similarities_use_case import (
    GetSimilaritiesUseCase,
)
from data_agent.similarity.similarity_storage.similarity_storage import (
    SimilarityStorage,
)


@fixture
def similarity_storage():
    return mock.Mock(spec=SimilarityStorage)


def test_get_similarities_use_case_execute_success(
    similarity_storage: SimilarityStorage,
):
    query = "Please create a low risk basket without stablecoins."
    documents = [
        SimilarityDocument(page_content="page content 1", metadata="metadata 1"),
        SimilarityDocument(page_content="page content 2", metadata="metadata 2"),
    ]

    similarity_storage.similarity_search.return_value = documents

    use_case = GetSimilaritiesUseCase(similarity_storage)

    serialized, retrieved_docs = use_case.execute(query)

    assert serialized == (
        "Source: metadata 1\nContent: page content 1\n\n"
        "Source: metadata 2\nContent: page content 2"
    )
    assert retrieved_docs == documents

    similarity_storage.similarity_search.assert_called_once_with(query)
