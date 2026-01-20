from abc import ABC, abstractmethod
from typing import Literal

from api.protocol.asset import Asset
from api.protocol.asset_category import AssetCategory
from api.similarity.similarity_document import SimilarityDocument


class AssetSimilarityRepository(ABC):
    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def similarity_search(
        self,
        name_or_ticker: str | None,
        type: Literal["BASKET", "TOKEN"] | None,
        categories: list[AssetCategory] | None,
    ) -> list[Asset]:
        raise NotImplementedError

    @abstractmethod
    async def get(self, ids: list[str]) -> list[SimilarityDocument]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_field(self, name: str, value: str) -> list[SimilarityDocument]:
        raise NotImplementedError

    @abstractmethod
    def set(self, documents: list[SimilarityDocument]) -> None:
        raise NotImplementedError
