from typing import Literal
from api.protocol.asset_category import AssetCategory
from api.similarity.asset_similarity_repository import (
    AssetSimilarityRepository,
)
from api.protocol.asset import Asset


class GetSimilarAssetsUseCase:
    def __init__(self, storage: AssetSimilarityRepository):
        self.storage = storage

    async def execute(
        self,
        name_or_ticker: str | None,
        type: Literal["BASKET", "TOKEN"] | None,
        categories: list[AssetCategory] | None,
    ) -> list[Asset]:
        return await self.storage.similarity_search(name_or_ticker, type, categories)
