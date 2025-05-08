from typing import Any, TypedDict
from langchain_core.embeddings import Embeddings

from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

from data_agent.similarity.similarity_document import SimilarityDocument
from data_agent.similarity.similarity_storage.similarity_storage import (
    SimilarityStorage,
)


class Configuration(TypedDict):
    qdrant_collection: str
    qdrant_url: str
    qdrant_api_key: str


class QdrantLangChainSimilarityStorage(SimilarityStorage):
    def __init__(
        self,
        configuration: Configuration,
        qdrant_client: type[QdrantClient],
        qdrant_vector_store: type[QdrantVectorStore],
        embeddings: Embeddings,
    ):
        client = qdrant_client(
            url=configuration["qdrant_url"],
            api_key=configuration["qdrant_api_key"],
            prefer_grpc=True,
        )

        # TODO: Keep the same collection, just update documents by their id somehow
        client.recreate_collection(  # safely drops if exists
            collection_name=configuration["qdrant_collection"],
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
        )

        self.qdrant = qdrant_vector_store(
            client=client,
            collection_name=configuration["qdrant_collection"],
            embedding=embeddings,
        )

        self.embeddings = embeddings

    def similarity_search(self, query: str):
        """
        Performs a similarity search in the Qdrant vector store."""

        return [
            self.__map_document_to_similarity_document(doc)
            for doc in self.qdrant.similarity_search(query)
        ]

    def set(self, documents: list[SimilarityDocument]):
        print(f"Upserting {len(documents)} documents to Qdrant")
        """
        Upserts the documents into the Qdrant vector store.
        """
        self.qdrant.add_documents(
            [
                self.__map_similarity_document_to_document(document)
                for document in documents
            ],
        )

    def __map_document_to_similarity_document(
        self, document: Document
    ) -> SimilarityDocument:
        return SimilarityDocument(
            page_content=document.page_content,
            metadata=document.metadata or None,
            id=document.id,
        )

    def __map_similarity_document_to_document(
        self, document: SimilarityDocument
    ) -> Document:
        return Document(
            id=document.id,
            page_content=document.page_content,
            metadata=document.metadata or dict(),
        )
