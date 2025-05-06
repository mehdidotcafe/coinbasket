from abc import ABC, abstractmethod

from data_agent.similarity.similarity_document import SimilarityDocument


class SimilarityStorage(ABC):
    @abstractmethod
    def similarity_search(self, query: str) -> list[SimilarityDocument]:
        raise NotImplementedError
