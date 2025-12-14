from abc import ABC, abstractmethod
from typing import Any

from api.similarity.similarity_document import SimilarityDocument


class SimilarityStorage(ABC):
    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def similarity_search(
        self, query: str, filters: dict[str, Any] | None
    ) -> list[SimilarityDocument]:
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
