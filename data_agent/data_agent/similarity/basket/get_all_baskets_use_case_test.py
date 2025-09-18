from decimal import Decimal
from unittest import mock
from data_agent.similarity.exception.invalid_similarity_document import (
    InvalidSimilarityDocument,
)
from data_agent.similarity.similarity_document import SimilarityDocument
from data_agent.similarity.similarity_storage.similarity_storage import (
    SimilarityStorage,
)
from data_agent.similarity.basket.get_all_baskets_use_case import GetAllBasketsUseCase
from protocol.basket import Basket
from protocol.token import Token
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
            page_content="page content 1",
            metadata={
                "version": 2,
                "type": "basket",
                "source": {
                    "denomination": "10.0",
                    "tokens": [
                        {
                            "display_name": "Bitcoin",
                            "address": "0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
                            "id": "bsc:0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
                            "ticker": "BTC",
                            "name": "Binance Pegged Bitcoin",
                        },
                        {
                            "display_name": "Ethereum",
                            "address": "0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
                            "id": "bsc:0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
                            "ticker": "ETH",
                            "name": "Binance Pegged Ethereum",
                        },
                    ],
                    "description": "This curated basket offers broad exposure to the crypto market through a selection of established, high-liquidity digital assets spanning different blockchain ecosystems. It is designed to balance long-term value preservation with growth potential, reflecting both foundational and emerging trends in decentralized technology. The combination supports diversification across transaction layers, use cases, and network adoption, making it a resilient core holding for crypto-oriented portfolios.",
                    "id": "2bb6425b-a9ee-4292-89c8-c1f0c7a5cb70",
                    "display_name": "Big4",
                    "ticker": "B4",
                    "name": "Big4",
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
            denomination=Decimal("10.0"),
            tokens=[
                Token(
                    address="0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
                    id="bsc:0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
                    name="Binance Pegged Bitcoin",
                    display_name="Bitcoin",
                    ticker="BTC",
                ),
                Token(
                    address="0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
                    id="bsc:0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
                    name="Binance Pegged Ethereum",
                    display_name="Ethereum",
                    ticker="ETH",
                ),
            ],
        )
    ]
    basket_repository.get_by_field.assert_awaited_once_with(name="type", value="basket")
