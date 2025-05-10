from typing import Union

from data_agent.similarity.similarity_document import SimilarityDocument
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

    # TODO: Current use case does NOT remove documents from the storage if not in the data source (use qdrant `scroll` API)
    def execute(self):
        for data_source in self.data_sources:
            documents = data_source.get()

            stored_documents = self.similarity_storage.get(
                [doc.id for doc in documents]
            )

            documents_to_update = self.filter_documents_to_update(
                documents, stored_documents
            )

            if (len(documents_to_update)) > 0:
                print(
                    f"Updating {data_source.__class__.__name__} documents in the storage."
                )
                self.similarity_storage.set(documents_to_update)
            else:
                print(f"No update for datasource {data_source.__class__.__name__}.")

    def filter_documents_to_update(
        self,
        documents: list[SimilarityDocument],
        stored_documents: list[SimilarityDocument],
    ) -> list[SimilarityDocument]:
        return [
            doc
            for doc in documents
            if doc.id
            not in [
                stored_doc.id
                for stored_doc in stored_documents
                if stored_doc.id == doc.id
                and stored_doc.metadata["version"] >= doc.metadata["version"]
            ]
        ]
