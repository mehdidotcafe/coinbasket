from unittest import mock
from api.asset.get_asset_by_id_use_case import GetAssetByIdUseCase
from api.similarity.exception.invalid_similarity_document import (
    InvalidSimilarityDocument,
)
from api.similarity.similarity_document import SimilarityDocument
from api.similarity.asset_similarity_repository import (
    AssetSimilarityRepository,
)
from pytest import fixture, mark, raises
from api.protocol.token import Token
from api.protocol.fixture.basket import test_basket


@fixture
def asset_repository():
    return mock.Mock(spec=AssetSimilarityRepository)


@fixture
def use_case(asset_repository: AssetSimilarityRepository):
    return GetAssetByIdUseCase(asset_repository=asset_repository)


@mark.asyncio
async def test_get_asset_by_id_use_case_not_found(
    asset_repository: AssetSimilarityRepository, use_case: GetAssetByIdUseCase
):
    asset_repository.get_by_field.return_value = None

    result = await use_case.execute("123456")

    assert not result

    asset_repository.get_by_field.assert_called_once_with(
        name="source.id", value="123456"
    )


@mark.asyncio
async def test_get_asset_by_id_use_case_found_without_metadata(
    asset_repository: AssetSimilarityRepository, use_case: GetAssetByIdUseCase
):
    asset_repository.get_by_field.return_value = [
        SimilarityDocument(
            page_content="page content 1",
            metadata=None,
            id="1",
        ),
    ]

    with raises(InvalidSimilarityDocument):
        await use_case.execute("123456")


@mark.asyncio
async def test_get_asset_by_id_use_case_found_basket(
    asset_repository: AssetSimilarityRepository, use_case: GetAssetByIdUseCase
):
    asset_repository.get_by_field.return_value = [
        SimilarityDocument(
            page_content="page content 1",
            metadata={
                "version": 2,
                "type": "basket",
                "source": test_basket.to_dict(),
                "_id": "2bb6425b-a9ee-4292-89c8-c1f0c7a5cb70",
                "_collection_name": "datasets",
            },
            id="1",
        ),
    ]

    result = await use_case.execute("123456A")

    assert result == test_basket

    asset_repository.get_by_field.assert_called_once_with(
        name="source.id", value="123456a"
    )


@mark.asyncio
async def test_get_asset_by_id_use_case_found_token(
    asset_repository: AssetSimilarityRepository, use_case: GetAssetByIdUseCase
):
    asset_repository.get_by_field.return_value = [
        SimilarityDocument(
            page_content="page content 1",
            metadata={
                "version": 2,
                "type": "token",
                "source": {
                    "address": "0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
                    "id": "bsc:0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
                    "name": "Binance Pegged Bitcoin",
                    "display_name": "Bitcoin",
                    "ticker": "BTC",
                    "description": "Binance Pegged Bitcoin is a token that represents Bitcoin on the Binance Smart Chain.",
                    "categories": ["peg", "bitcoin"],
                    "decimals": 18,
                    "logo_uri": "https://example.com/btc-logo.png",
                    "type": "TOKEN",
                },
                "_id": "2bb6425b-a9ee-4292-89c8-c1f0c7a5cb70",
                "_collection_name": "datasets",
            },
            id="123456",
        ),
    ]

    result = await use_case.execute("123456A")

    assert result == Token(
        address="0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
        id="bsc:0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
        name="Binance Pegged Bitcoin",
        display_name="Bitcoin",
        ticker="BTC",
        description="Binance Pegged Bitcoin is a token that represents Bitcoin on the Binance Smart Chain.",
        categories=["peg", "bitcoin"],
        decimals=18,
        logo_uri="https://example.com/btc-logo.png",
    )

    asset_repository.get_by_field.assert_called_once_with(
        name="source.id", value="123456a"
    )
