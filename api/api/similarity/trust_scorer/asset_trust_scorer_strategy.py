from abc import ABC, abstractmethod
from typing import Any


class AssetTrustScorerStrategy(ABC):
    @abstractmethod
    async def score(self, raw_asset: dict[str, Any]) -> int:
        raise NotImplementedError
