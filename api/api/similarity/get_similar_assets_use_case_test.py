from unittest import mock
from api.protocol.token import Token
from pytest import fixture, mark, raises
from api.similarity.exception.invalid_similarity_document import (
    InvalidSimilarityDocument,
)
from api.similarity.similarity_document import SimilarityDocument
from api.similarity.get_similar_assets_use_case import (
    GetSimilarAssetsUseCase,
)
from api.similarity.similarity_storage.similarity_storage import (
    SimilarityStorage,
)

from api.protocol.fixture.basket import test_basket


@fixture
def similarity_storage():
    return mock.Mock(spec=SimilarityStorage)


@mark.asyncio
async def test_get_similar_assets_use_case_fail_document_without_metadata(
    similarity_storage: SimilarityStorage,
):
    query = "bitcoin"
    documents = [
        SimilarityDocument(
            page_content="page content 1",
            metadata={},
            id="1",
        ),
    ]

    similarity_storage.similarity_search.return_value = documents

    use_case = GetSimilarAssetsUseCase(similarity_storage)

    with raises(InvalidSimilarityDocument):
        await use_case.execute(query, None)


@mark.asyncio
async def test_get_similar_assets_use_case_fail_document_with_invalid_type(
    similarity_storage: SimilarityStorage,
):
    query = "bitcoin"
    documents = [
        SimilarityDocument(
            page_content="page content 1",
            metadata={
                "version": 2,
                "type": "INVALID",
                "source": {
                    "display_name": "Bitcoin",
                    "address": "0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
                    "id": "bsc:0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
                    "ticker": "BTCB",
                    "name": "Binance Pegged Bitcoin",
                    "type": "INVALID",
                },
                "_id": "c535ce3f-d363-67f4-3619-e822a9776ec2",
                "_collection_name": "datasets",
            },
            id="1",
        ),
    ]

    similarity_storage.similarity_search.return_value = documents

    use_case = GetSimilarAssetsUseCase(similarity_storage)

    with raises(InvalidSimilarityDocument):
        await use_case.execute(query, None)


@mark.asyncio
async def test_get_similar_assets_use_case_execute_with_tokens(
    similarity_storage: SimilarityStorage,
):
    query = "bitcoin"
    documents = [
        SimilarityDocument(
            page_content="page content 1",
            metadata={
                "version": 2,
                "type": "token",
                "source": {
                    "display_name": "Bitcoin",
                    "address": "0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
                    "id": "bsc:0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
                    "ticker": "BTCB",
                    "name": "Binance Pegged Bitcoin",
                    "description": "Binance Pegged Bitcoin is a token that represents Bitcoin on the Binance Smart Chain.",
                    "categories": ["peg", "bitcoin"],
                    "decimals": 18,
                    "logo_uri": "https://example.com/btc-logo.png",
                    "type": "TOKEN",
                },
                "_id": "c535ce3f-d363-67f4-3619-e822a9776ec2",
                "_collection_name": "datasets",
            },
            id="1",
        ),
        SimilarityDocument(
            page_content="page content 2",
            metadata={
                "version": 2,
                "type": "token",
                "source": {
                    "display_name": "Tau Bitcoin",
                    "address": "0x2cD1075682b0FCCaADd0Ca629e138E64015Ba11c",
                    "id": "bsc:0x2cD1075682b0FCCaADd0Ca629e138E64015Ba11c",
                    "ticker": "tBTC",
                    "name": "Tau Bitcoin",
                    "description": "Tau Bitcoin is a token that represents Bitcoin on the Tau blockchain.",
                    "categories": ["peg", "bitcoin"],
                    "decimals": 18,
                    "logo_uri": "https://example.com/tbtc-logo.png",
                    "type": "TOKEN",
                },
                "_id": "f6dd0b6e-97c1-1034-4b3e-2930f4e4116b",
                "_collection_name": "datasets",
            },
            id="2",
        ),
    ]

    similarity_storage.similarity_search.return_value = documents

    use_case = GetSimilarAssetsUseCase(similarity_storage)

    assets = await use_case.execute(query, "TOKEN")

    assert assets == [
        Token(
            address="0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
            id="bsc:0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
            name="Binance Pegged Bitcoin",
            display_name="Bitcoin",
            ticker="BTCB",
            description="Binance Pegged Bitcoin is a token that represents Bitcoin on the Binance Smart Chain.",
            categories=["peg", "bitcoin"],
            decimals=18,
            logo_uri="https://example.com/btc-logo.png",
        ),
        Token(
            address="0x2cD1075682b0FCCaADd0Ca629e138E64015Ba11c",
            id="bsc:0x2cD1075682b0FCCaADd0Ca629e138E64015Ba11c",
            name="Tau Bitcoin",
            display_name="Tau Bitcoin",
            ticker="tBTC",
            description="Tau Bitcoin is a token that represents Bitcoin on the Tau blockchain.",
            categories=["peg", "bitcoin"],
            decimals=18,
            logo_uri="https://example.com/tbtc-logo.png",
        ),
    ]

    similarity_storage.similarity_search.assert_called_once_with(
        query, {"type": "token"}
    )


@mark.asyncio
async def test_get_similar_assets_use_case_execute_with_baskets(
    similarity_storage: SimilarityStorage,
):
    query = "bitcoin"
    documents = [
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

    similarity_storage.similarity_search.return_value = documents

    use_case = GetSimilarAssetsUseCase(similarity_storage)

    assets = await use_case.execute(query, "BASKET")

    assert assets == [test_basket]

    similarity_storage.similarity_search.assert_called_once_with(
        query, {"type": "basket"}
    )
