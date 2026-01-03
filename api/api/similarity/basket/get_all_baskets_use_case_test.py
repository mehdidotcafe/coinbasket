from unittest import mock
from api.similarity.exception.invalid_similarity_document import (
    InvalidSimilarityDocument,
)
from api.similarity.similarity_document import SimilarityDocument
from api.similarity.similarity_storage.similarity_storage import (
    SimilarityStorage,
)
from api.similarity.basket.get_all_baskets_use_case import GetAllBasketsUseCase
from api.protocol.basket import Basket
from pytest import fixture, mark, raises


@fixture
def basket_repository():
    return mock.Mock(spec=SimilarityStorage)


@fixture
def use_case(basket_repository: SimilarityStorage):
    return GetAllBasketsUseCase(basket_repository)


@mark.asyncio
async def test_get_all_baskets_use_case_no_metadata_document(
    basket_repository: SimilarityStorage, use_case: GetAllBasketsUseCase
):
    basket_repository.get_by_field.return_value = [
        SimilarityDocument(
            page_content="page content 1",
            metadata=None,
            id="1",
        ),
    ]

    with raises(InvalidSimilarityDocument):
        await use_case.execute()


@mark.asyncio
async def test_get_all_baskets_use_case_no_basket_document(
    basket_repository: SimilarityStorage, use_case: GetAllBasketsUseCase
):
    basket_repository.get_by_field.return_value = [
        SimilarityDocument(
            page_content="page content 1",
            metadata={"type": "token"},
            id="1",
        ),
    ]

    with raises(InvalidSimilarityDocument):
        await use_case.execute()


@mark.asyncio
async def test_get_all_baskets_use_case_success(
    basket_repository: SimilarityStorage, use_case: GetAllBasketsUseCase
):
    basket_repository.get_by_field.return_value = [
        SimilarityDocument(
            page_content="page content 2",
            metadata={
                "version": 2,
                "type": "basket",
                "source": {
                    "description": "Dummy basket.",
                    "id": "11111111-a9ee-4292-89c8-c1f0c7a5cb70",
                    "display_name": "DUMMY",
                    "ticker": "DUMMY",
                    "name": "DUMMY",
                    "address": "0xDUMMYADDRESS",
                    "decimals": 18,
                    "categories": ["basket"],
                },
                "_id": "11111111-a9ee-4292-89c8-c1f0c7a5cb70",
                "_collection_name": "datasets",
            },
            id="1",
        ),
        SimilarityDocument(
            page_content="page content 1",
            metadata={
                "version": 2,
                "type": "basket",
                "source": {
                    "description": "This curated basket offers broad exposure to the crypto market through a selection of established, high-liquidity digital assets spanning different blockchain ecosystems. It is designed to balance long-term value preservation with growth potential, reflecting both foundational and emerging trends in decentralized technology. The combination supports diversification across transaction layers, use cases, and network adoption, making it a resilient core holding for crypto-oriented portfolios.",
                    "id": "2bb6425b-a9ee-4292-89c8-c1f0c7a5cb70",
                    "display_name": "Big4",
                    "ticker": "B4",
                    "name": "Big4",
                    "address": "0xBIG4ADDRESS",
                    "decimals": 18,
                    "categories": ["basket"],
                },
                "_id": "2bb6425b-a9ee-4292-89c8-c1f0c7a5cb70",
                "_collection_name": "datasets",
            },
            id="1",
        ),
    ]

    result = await use_case.execute()

    assert result == [
        Basket(
            id="2bb6425b-a9ee-4292-89c8-c1f0c7a5cb70",
            display_name="Big4",
            name="Big4",
            ticker="B4",
            description="This curated basket offers broad exposure to the crypto market through a selection of established, high-liquidity digital assets spanning different blockchain ecosystems. It is designed to balance long-term value preservation with growth potential, reflecting both foundational and emerging trends in decentralized technology. The combination supports diversification across transaction layers, use cases, and network adoption, making it a resilient core holding for crypto-oriented portfolios.",
            decimals=18,
            address="0xBIG4ADDRESS",
            categories=["basket"],
        ),
        Basket(
            id="11111111-a9ee-4292-89c8-c1f0c7a5cb70",
            display_name="DUMMY",
            name="DUMMY",
            ticker="DUMMY",
            description="Dummy basket.",
            decimals=18,
            address="0xDUMMYADDRESS",
            categories=["basket"],
        ),
    ]
    basket_repository.get_by_field.assert_awaited_once_with(name="type", value="basket")
