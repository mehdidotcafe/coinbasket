from abc import ABC, abstractmethod

from data_agent.similarity.similarity_document import SimilarityDocument


class SimilarityStorage(ABC):
    @abstractmethod
    def similarity_search(self, query: str) -> list[SimilarityDocument]:
        raise NotImplementedError

    @abstractmethod
    def set(self, documents: list[SimilarityDocument]) -> None:
        raise NotImplementedError
