from abc import ABC, abstractmethod

from api.similarity.asset_similarity import AssetSimilarity


class DataSource(ABC):
    @abstractmethod
    async def get(self) -> list[AssetSimilarity]:
        raise NotImplementedError

    @abstractmethod
    def version(self) -> int:
        raise NotImplementedError
