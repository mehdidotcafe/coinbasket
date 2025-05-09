from unittest import mock

from protocol.basket import Basket
from protocol.token import Token
from pytest import fixture

from data_agent.similarity.similarity_storage.similarity_storage import (
    SimilarityStorage,
)
from data_agent.similarity.similarity_document import SimilarityDocument
from data_agent.ingestion.ingest_data_use_case import IngestDataUseCase
from data_agent.ingestion.data_source.data_source import DataSource


@fixture
def similarity_storage():
    return mock.Mock(spec=SimilarityStorage)


@fixture
def token_data_source():
    return mock.Mock(spec=DataSource)


@fixture
def basket_data_source():
    return mock.Mock(spec=DataSource)


def test_ingest_data_use_case(
    similarity_storage: SimilarityStorage,
    token_data_source: DataSource,
    basket_data_source: DataSource,
):
    token_similarity_documents = [
        SimilarityDocument(
            metadata={
                "type": "token",
                "source": Token(
                    name="Wrapped BNB",
                    display_name="Wrapped BNB",
                    ticker="WBNB",
                    address="0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7",
                ),
            },
            page_content=""""
              name: Wrapped BNB
              display_name: Wrapped BNB
              ticker: WBNB
              address: 0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7
            """,
            id="97c8ba98-c869-4929-b048-27bc703693e4",
        )
    ]
    token_data_source.get.return_value = token_similarity_documents

    similarity_storage.get.return_value = []

    basket_similarity_documents = [
        SimilarityDocument(
            metadata={
                "type": "basket",
                "source": Basket(
                    name="Wrapped BNB",
                    description="Just BNB",
                    tokens=[
                        Token(
                            name="Wrapped BNB",
                            display_name="Wrapped BNB",
                            ticker="WBNB",
                            address="0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7",
                        )
                    ],
                ),
            },
            page_content="""
              name: Wrapped BNB
              tokens:
              1.  name: Wrapped BNB
                  display_name: Wrapped BNB
                  ticker: WBNB
                  address: 0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7
            """,
            id="8a9a8501-1123-43f5-88e3-6b526f8f9d19",
        )
    ]
    basket_data_source.get.return_value = basket_similarity_documents

    use_case = IngestDataUseCase(
        similarity_storage,
        [
            token_data_source,
            basket_data_source,
        ],
    )

    use_case.execute()

    token_data_source.get.assert_called_once()
    basket_data_source.get.assert_called_once()

    similarity_storage.assert_has_calls(
        [
            mock.call.get(["97c8ba98-c869-4929-b048-27bc703693e4"]),
            mock.call.set(token_similarity_documents),
            mock.call.get(["8a9a8501-1123-43f5-88e3-6b526f8f9d19"]),
            mock.call.set(basket_similarity_documents),
        ]
    )


def test_ingest_data_use_case_with_existing_documents_lower_version(
    similarity_storage: SimilarityStorage,
    token_data_source: DataSource,
):
    token_similarity_documents = [
        SimilarityDocument(
            metadata={"version": 2},
            page_content="page content 1",
            id="97c8ba98-c869-4929-b048-27bc703693e4",
        )
    ]
    token_data_source.get.return_value = token_similarity_documents

    similarity_storage.get.return_value = [
        SimilarityDocument(
            metadata={"version": 1},
            page_content="page content 1",
            id="97c8ba98-c869-4929-b048-27bc703693e4",
        )
    ]

    use_case = IngestDataUseCase(
        similarity_storage,
        [
            token_data_source,
        ],
    )

    use_case.execute()

    similarity_storage.set.assert_called_once_with(
        [
            SimilarityDocument(
                metadata={"version": 2},
                page_content="page content 1",
                id="97c8ba98-c869-4929-b048-27bc703693e4",
            )
        ]
    )


def test_ingest_data_use_case_with_existing_documents_same_version(
    similarity_storage: SimilarityStorage,
    token_data_source: DataSource,
):
    token_similarity_documents = [
        SimilarityDocument(
            metadata={"version": 1},
            page_content="page content 1",
            id="97c8ba98-c869-4929-b048-27bc703693e4",
        )
    ]
    token_data_source.get.return_value = token_similarity_documents

    similarity_storage.get.return_value = [
        SimilarityDocument(
            metadata={"version": 1},
            page_content="page content 1",
            id="97c8ba98-c869-4929-b048-27bc703693e4",
        )
    ]

    use_case = IngestDataUseCase(
        similarity_storage,
        [
            token_data_source,
        ],
    )

    use_case.execute()

    similarity_storage.set.assert_not_called()
