from abc import ABC, abstractmethod

from api.similarity.asset_similarity import TokenSimilarity
from pydantic import BaseModel


class TokenRepository(ABC):
    @abstractmethod
    async def get_by_address(self, address: str) -> TokenSimilarity | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_address_raw(self, address: str) -> BaseModel | None:
        raise NotImplementedError
