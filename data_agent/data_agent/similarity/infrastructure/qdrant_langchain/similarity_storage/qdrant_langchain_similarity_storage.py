from typing import TypedDict
from langchain_core.embeddings import Embeddings
from langchain_community.document_loaders import JSONLoader
from langchain_community.vectorstores import Qdrant
from langchain_core.documents import Document

from data_agent.similarity.similarity_document import SimilarityDocument
from data_agent.similarity.similarity_storage.similarity_storage import (
    SimilarityStorage,
)


class Configuration(TypedDict):
    qdrant_url: str
    qdrant_api_key: str


class QdrantLangChainSimilarityStorage(SimilarityStorage):
    def __init__(
        self, configuration: Configuration, qdrant: type[Qdrant], embeddings: Embeddings
    ):
        loader = JSONLoader(
            file_path="./data/selection.json",
            jq_schema=".",
            text_content=False,
        )

        docs = loader.load()

        self.qdrant = qdrant.from_documents(
            docs,
            embeddings,
            url=configuration["qdrant_url"],
            prefer_grpc=True,
            api_key=configuration["qdrant_api_key"],
            collection_name="dataset",
            force_recreate=True,
        )
        self.embeddings = embeddings

    def similarity_search(self, query: str):
        return [
            self.__map_document_to_similarity_document(doc)
            for doc in self.qdrant.similarity_search(query)
        ]

    def __map_document_to_similarity_document(
        self, document: Document
    ) -> SimilarityDocument:
        return SimilarityDocument(
            page_content=document.page_content,
            metadata=document.metadata or None,
        )
