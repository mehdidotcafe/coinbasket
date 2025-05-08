from abc import ABC, abstractmethod

from data_agent.similarity.similarity_document import SimilarityDocument


class DataSource(ABC):
    @abstractmethod
    def get(self) -> list[SimilarityDocument]:
        raise NotImplementedError

    @abstractmethod
    def version(self) -> int:
        raise NotImplementedError
