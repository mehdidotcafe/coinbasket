from typing import Any, TypedDict
from langchain_core.embeddings import Embeddings

from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document
from qdrant_client import AsyncQdrantClient, QdrantClient, models
from qdrant_client.models import VectorParams, Distance, Record

from data_agent.similarity.similarity_document import SimilarityDocument
from data_agent.similarity.similarity_storage.similarity_storage import (
    SimilarityStorage,
)


class Configuration(TypedDict):
    qdrant_collection: str
    qdrant_url: str
    qdrant_port: int
    qdrant_grpc_port: int
    qdrant_api_key: str


class QdrantLangChainSimilarityStorage(SimilarityStorage):
    def __init__(
        self,
        configuration: Configuration,
        qdrant_client: type[QdrantClient],
        qdrant_vector_store: type[QdrantVectorStore],
        embeddings: Embeddings,
    ):
        self.client = qdrant_client(
            url=configuration["qdrant_url"],
            port=configuration["qdrant_port"],
            grpc_port=configuration["qdrant_grpc_port"],
            api_key=configuration["qdrant_api_key"],
            prefer_grpc=True,
        )
        self.async_client = AsyncQdrantClient(
            url=configuration["qdrant_url"],
            port=configuration["qdrant_port"],
            grpc_port=configuration["qdrant_grpc_port"],
            api_key=configuration["qdrant_api_key"],
            prefer_grpc=True,
        )

        if self.client.collection_exists(configuration["qdrant_collection"]) is False:
            self.client.create_collection(
                collection_name=configuration["qdrant_collection"],
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
            )

        self.qdrant = qdrant_vector_store(
            client=self.client,
            collection_name=configuration["qdrant_collection"],
            embedding=embeddings,
        )

        self.configuration = configuration
        self.embeddings = embeddings

    async def similarity_search(self, query: str):
        """
        Performs a similarity search in the Qdrant vector store."""

        return [
            self.__map_document_to_similarity_document(doc)
            for doc in await self.qdrant.asimilarity_search(query, 10)
        ]

    def get(self, ids: list[str]):
        return [
            self.__map_document_to_similarity_document(doc)
            for doc in self.qdrant.get_by_ids(ids)
        ]

    async def get_by_field(self, name: str, value: str) -> list[SimilarityDocument]:
        records: list[Record] = []
        offset = None

        while True:
            points, next_offset = await self.async_client.scroll(
                collection_name=self.configuration["qdrant_collection"],
                scroll_filter=models.Filter(
                    should=[
                        models.FieldCondition(
                            key=f"metadata.{name}",
                            match=models.MatchValue(value=value),
                        ),
                    ]
                ),
                limit=100,
                offset=offset,
            )

            records.extend(points)

            if next_offset is None:
                break
            offset = next_offset

        return [
            self.__map_record_to_similarity_document(record.payload, record.id)
            for record in records
            if record.payload
        ]

    def set(self, documents: list[SimilarityDocument]):
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
            metadata=document.metadata,
            id=document.metadata["_id"],
        )

    def __map_record_to_similarity_document(
        self, record_payload: dict[str, Any], record_id: int | str
    ) -> SimilarityDocument:
        return SimilarityDocument(
            page_content=record_payload["page_content"],
            metadata=record_payload["metadata"],
            id=str(record_id),
        )

    def __map_similarity_document_to_document(
        self, document: SimilarityDocument
    ) -> Document:
        return Document(
            id=document.id,
            page_content=document.page_content,
            metadata=document.metadata or dict(),
        )
