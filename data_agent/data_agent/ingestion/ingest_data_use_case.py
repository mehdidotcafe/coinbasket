from typing import Union

from data_agent.similarity.similarity_storage.similarity_storage import (
    SimilarityStorage,
)
from data_agent.ingestion.data_source.data_source import DataSource
from protocol.basket import Basket
from protocol.token import Token

type Data = Union[list[Token], list[Basket]]


class IngestDataUseCase:
    def __init__(
        self,
        similarity_storage: SimilarityStorage,
        data_sources: list[DataSource],
    ):
        self.similarity_storage = similarity_storage
        self.data_sources = data_sources

    def execute(self):
        for data_source in self.data_sources:
            self.similarity_storage.set(data_source.get())
