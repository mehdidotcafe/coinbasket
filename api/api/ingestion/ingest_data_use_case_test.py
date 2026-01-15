from unittest import mock

from api.shared.id_generator.id_generator import IdGenerator
from api.similarity.asset_similarity import TokenSimilarity, BasketSimilarity
from pytest import fixture, mark

from api.similarity.asset_similarity_repository import AssetSimilarityRepository
from api.similarity.similarity_document import SimilarityDocument
from api.ingestion.ingest_data_use_case import IngestDataUseCase
from api.ingestion.data_source.data_source import DataSource


@fixture
def similarity_storage():
    return mock.Mock(spec=AssetSimilarityRepository)


@fixture
def id_generator():
    generator = mock.Mock(spec=IdGenerator)

    generator.generate_id.side_effect = [
        "97c8ba98-c869-4929-b048-27bc703693e4",
        "8a9a8501-1123-43f5-88e3-6b526f8f9d19",
    ]

    return generator


@fixture
def token_data_source():
    data_source = mock.Mock(spec=DataSource)

    data_source.version.return_value = 1

    return data_source


@fixture
def basket_data_source():
    data_source = mock.Mock(spec=DataSource)

    data_source.version.return_value = 2

    return data_source


@mark.asyncio
async def test_ingest_data_use_case_success(
    similarity_storage: AssetSimilarityRepository,
    token_data_source: DataSource,
    basket_data_source: DataSource,
    id_generator: IdGenerator,
):
    token_similarity = [
        TokenSimilarity(
            id="bsc:0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7",
            name="Wrapped BNB",
            display_name="Wrapped BNB",
            ticker="WBNB",
            address="0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7",
            description="Wrapped BNB is a wrapped version of Binance Coin (BNB) on the Binance Smart Chain.",
            categories=["wrapped", "bnb"],
            decimals=18,
            logo_uri="https://example.com/wbnb-logo.png",
            market_cap_usd=5_000_000_000,
            is_canonical=True,
        )
    ]
    token_data_source.get.return_value = token_similarity

    similarity_storage.get.return_value = []

    basket_similarity = [
        BasketSimilarity(
            id="bsc:0x12345567890abcdef1234567890abcdef1234567",
            name="Wrapped BNB",
            display_name="Wrapped BNB",
            ticker="WBNB",
            description="Just BNB",
            categories=["basket"],
            decimals=18,
            address="0x12345567890abcdef1234567890abcdef1234567",
            market_cap_usd=10_000_000_000,
            is_canonical=True,
        )
    ]

    basket_data_source.get.return_value = basket_similarity

    use_case = IngestDataUseCase(
        similarity_storage=similarity_storage,
        id_generator=id_generator,
        data_sources=[
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
            mock.call.set(
                [
                    SimilarityDocument(
                        metadata={
                            "source": {
                                "id": "bsc:0xb31f66aa3c1e785363f0875a1b74e27b85fd66c7",
                                "name": "Wrapped BNB",
                                "display_name": "Wrapped BNB",
                                "ticker": "WBNB",
                                "address": "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7",
                                "description": "Wrapped BNB is a wrapped version of Binance Coin (BNB) on the Binance Smart Chain.",
                                "decimals": 18,
                                "logo_uri": "https://example.com/wbnb-logo.png",
                                "categories": ["wrapped", "bnb"],
                                "type": "TOKEN",
                                "market_cap_usd": 5_000_000_000,
                                "is_canonical": True,
                            },
                            "type": "token",
                            "version": 1,
                        },
                        page_content="\nname: Wrapped BNB\ndisplay_name: Wrapped BNB\ndescription: Wrapped BNB is a wrapped version of Binance Coin (BNB) on the Binance Smart Chain.\nticker: WBNB\naddress: 0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7\ncategories: wrapped, bnb\n",
                        id="97c8ba98-c869-4929-b048-27bc703693e4",
                    )
                ]
            ),
            mock.call.get(["8a9a8501-1123-43f5-88e3-6b526f8f9d19"]),
            mock.call.set(
                [
                    SimilarityDocument(
                        metadata={
                            "type": "basket",
                            "version": 2,
                            "source": {
                                "id": "bsc:0x12345567890abcdef1234567890abcdef1234567",
                                "name": "Wrapped BNB",
                                "display_name": "Wrapped BNB",
                                "ticker": "WBNB",
                                "address": "0x12345567890abcdef1234567890abcdef1234567",
                                "description": "Just BNB",
                                "decimals": 18,
                                "logo_uri": None,
                                "categories": ["basket"],
                                "type": "BASKET",
                                "market_cap_usd": 10000000000,
                                "is_canonical": True,
                            },
                        },
                        page_content="\nname: Wrapped BNB\ndisplay_name: Wrapped BNB\ndescription: Just BNB\nticker: WBNB\naddress: 0x12345567890abcdef1234567890abcdef1234567\ncategories: basket\n",
                        id="8a9a8501-1123-43f5-88e3-6b526f8f9d19",
                    )
                ],
            ),
        ]
    )


@mark.asyncio
async def test_ingest_data_use_case_with_existing_documents_lower_version(
    similarity_storage: AssetSimilarityRepository,
    token_data_source: DataSource,
    id_generator: IdGenerator,
):
    token_data_source.get.return_value = [
        TokenSimilarity(
            id="bsc:0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7",
            name="Wrapped BNB",
            display_name="Wrapped BNB",
            ticker="WBNB",
            address="0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7",
            description="Wrapped BNB is a wrapped version of Binance Coin (BNB) on the Binance Smart Chain.",
            categories=["wrapped", "bnb"],
            decimals=18,
            logo_uri="https://example.com/wbnb-logo.png",
            market_cap_usd=5_000_000_000,
            is_canonical=True,
        )
    ]

    similarity_storage.get.return_value = [
        SimilarityDocument(
            metadata={"version": 0},
            page_content="page content 1",
            id="97c8ba98-c869-4929-b048-27bc703693e4",
        )
    ]

    use_case = IngestDataUseCase(
        similarity_storage=similarity_storage,
        id_generator=id_generator,
        data_sources=[
            token_data_source,
        ],
    )

    await use_case.execute()

    similarity_storage.set.assert_called_once_with(
        [
            SimilarityDocument(
                metadata={
                    "source": mock.ANY,
                    "type": mock.ANY,
                    "version": 1,
                },
                page_content=mock.ANY,
                id=mock.ANY,
            )
        ]
    )


@mark.asyncio
async def test_ingest_data_use_case_with_existing_documents_same_version(
    similarity_storage: AssetSimilarityRepository,
    token_data_source: DataSource,
    id_generator: IdGenerator,
):
    token_similarity_documents = [
        TokenSimilarity(
            id="bsc:0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7",
            name="Wrapped BNB",
            display_name="Wrapped BNB",
            ticker="WBNB",
            address="0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7",
            description="Wrapped BNB is a wrapped version of Binance Coin (BNB) on the Binance Smart Chain.",
            categories=["wrapped", "bnb"],
            decimals=18,
            logo_uri="https://example.com/wbnb-logo.png",
            market_cap_usd=5_000_000_000,
            is_canonical=True,
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
        similarity_storage=similarity_storage,
        id_generator=id_generator,
        data_sources=[
            token_data_source,
        ],
    )

    await use_case.execute()

    similarity_storage.set.assert_not_called()


@mark.asyncio
async def test_ingest_data_use_case_with_datasource_throw(
    similarity_storage: AssetSimilarityRepository,
    token_data_source: DataSource,
    id_generator: IdGenerator,
):
    token_data_source.get.side_effect = Exception("Data source error")

    use_case = IngestDataUseCase(
        similarity_storage=similarity_storage,
        id_generator=id_generator,
        data_sources=[
            token_data_source,
        ],
    )

    await use_case.execute()
