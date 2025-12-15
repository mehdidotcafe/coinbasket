from decimal import Decimal
from unittest import mock

from api.protocol.basket import Basket
from api.protocol.token import Token
from pytest import fixture, mark

from api.similarity.similarity_storage.similarity_storage import (
    SimilarityStorage,
)
from api.similarity.similarity_document import SimilarityDocument
from api.ingestion.ingest_data_use_case import IngestDataUseCase
from api.ingestion.data_source.data_source import DataSource


@fixture
def similarity_storage():
    return mock.Mock(spec=SimilarityStorage)


@fixture
def token_data_source():
    return mock.Mock(spec=DataSource)


@fixture
def basket_data_source():
    return mock.Mock(spec=DataSource)


@mark.asyncio
async def test_ingest_data_use_case(
    similarity_storage: SimilarityStorage,
    token_data_source: DataSource,
    basket_data_source: DataSource,
):
    token_similarity_documents = [
        SimilarityDocument(
            metadata={
                "type": "token",
                "source": Token(
                    id="bsc:0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7",
                    name="Wrapped BNB",
                    display_name="Wrapped BNB",
                    ticker="WBNB",
                    address="0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7",
                    description="Wrapped BNB is a wrapped version of Binance Coin (BNB) on the Binance Smart Chain.",
                    categories=["wrapped", "bnb"],
                    decimals=18,
                    logo_uri="https://example.com/wbnb-logo.png",
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
                    id="9760131e-8ca8-4d36-a636-2720e1d21bc7",
                    name="Wrapped BNB",
                    display_name="Wrapped BNB",
                    ticker="WBNB",
                    description="Just BNB",
                    denomination=Decimal("1.0"),
                    tokens=[
                        Token(
                            id="bsc:0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7",
                            name="Wrapped BNB",
                            display_name="Wrapped BNB",
                            ticker="WBNB",
                            address="0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7",
                            description="Wrapped BNB is a wrapped version of Binance Coin (BNB) on the Binance Smart Chain.",
                            categories=["wrapped", "bnb"],
                            decimals=18,
                            logo_uri="https://example.com/wbnb-logo.png",
                        )
                    ],
                ),
            },
            page_content="""
              name: Wrapped BNB
              display_name: Wrapped BNB
              ticker: WBNB
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

    await use_case.execute()

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


@mark.asyncio
async def test_ingest_data_use_case_with_existing_documents_lower_version(
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

    await use_case.execute()

    similarity_storage.set.assert_called_once_with(
        [
            SimilarityDocument(
                metadata={"version": 2},
                page_content="page content 1",
                id="97c8ba98-c869-4929-b048-27bc703693e4",
            )
        ]
    )


@mark.asyncio
async def test_ingest_data_use_case_with_existing_documents_same_version(
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

    await use_case.execute()

    similarity_storage.set.assert_not_called()


@mark.asyncio
async def test_ingest_data_use_case_with_datasource_throw(
    similarity_storage: SimilarityStorage,
    token_data_source: DataSource,
):
    token_data_source.get.side_effect = Exception("Data source error")

    use_case = IngestDataUseCase(
        similarity_storage,
        [
            token_data_source,
        ],
    )

    await use_case.execute()
