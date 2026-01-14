from unittest import mock
from api.protocol.asset import Asset
from api.protocol.asset_category import AssetCategory
from api.similarity.get_similar_assets_use_case import (
    GetSimilarAssetsUseCase,
)
from api.similarity.asset_similarity_repository import (
    AssetSimilarityRepository,
)

from api.protocol.fixture.basket import test_basket
from api.protocol.fixture.token import btc_token
from pytest import fixture, mark


@fixture
def similarity_storage():
    return mock.Mock(spec=AssetSimilarityRepository)


@mark.asyncio
async def test_get_similar_assets_use_case_execute_with_tokens(
    similarity_storage: AssetSimilarityRepository,
):
    query = "bitcoin"
    categories: list[AssetCategory] = ["DePIN"]
    documents: list[Asset] = [btc_token, test_basket]

    similarity_storage.similarity_search.return_value = documents

    use_case = GetSimilarAssetsUseCase(similarity_storage)

    assets = await use_case.execute(query, "TOKEN", categories)

    assert assets == [
        btc_token,
        test_basket,
    ]

    similarity_storage.similarity_search.assert_called_once_with(
        query, "TOKEN", ["DePIN"]
    )
