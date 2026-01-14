from typing import Any, Literal, TypedDict, cast
import math
from api.protocol.asset import Asset
from api.protocol.basket import Basket
from api.protocol.token import Token
from api.similarity.exception.invalid_similarity_document import (
    InvalidSimilarityDocument,
)
from langchain_core.embeddings import Embeddings

from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document
from qdrant_client import AsyncQdrantClient, QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    Record,
    Filter,
    FieldCondition,
    MatchValue,
    Condition,
    OrderBy,
    Direction,
)
from qdrant_client.http.models import PayloadSchemaType
from api.similarity.similarity_document import SimilarityDocument
from api.similarity.asset_similarity_repository import (
    AssetSimilarityRepository,
)


class Configuration(TypedDict):
    qdrant_collection: str
    qdrant_url: str
    qdrant_port: int
    qdrant_grpc_port: int
    qdrant_api_key: str


class QdrantLangChainAssetSimilarityRepository(AssetSimilarityRepository):
    def __init__(
        self,
        configuration: Configuration,
        qdrant_client: type[QdrantClient],
        qdrant_async_client: type[AsyncQdrantClient],
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
        self.async_client = qdrant_async_client(
            url=configuration["qdrant_url"],
            port=configuration["qdrant_port"],
            grpc_port=configuration["qdrant_grpc_port"],
            api_key=configuration["qdrant_api_key"],
            prefer_grpc=True,
        )

        self.qdrant_vector_store = qdrant_vector_store
        self.configuration = configuration
        self.embeddings = embeddings

    def start(self):
        if (
            self.client.collection_exists(self.configuration["qdrant_collection"])
            is False
        ):
            self.client.create_collection(
                collection_name=self.configuration["qdrant_collection"],
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
            )
            self.client.create_payload_index(
                collection_name=self.configuration["qdrant_collection"],
                field_name="metadata.source.market_cap_usd",
                field_schema=PayloadSchemaType.INTEGER,
            )

        self.qdrant = self.qdrant_vector_store(
            client=self.client,
            collection_name=self.configuration["qdrant_collection"],
            embedding=self.embeddings,
        )

    async def similarity_search(
        self,
        name_or_ticker: str | None = None,
        type: Literal["BASKET", "TOKEN"] | None = None,
        categories: Any | None = None,
    ) -> list[Asset]:
        """
        Performs a similarity search in the Qdrant vector store."""
        fetch_limit = 100
        return_limit = 5
        must_conditions: list[Condition] = []

        if categories:
            must_conditions.extend(
                FieldCondition(
                    key="metadata.source.categories",
                    match=MatchValue(value=category),
                )
                for category in categories
            )

        if type:
            must_conditions.append(
                FieldCondition(
                    key="metadata.type",
                    match=MatchValue(value=type.lower()),
                )
            )

        if name_or_ticker:
            documents_with_score = await self.qdrant.asimilarity_search_with_score(
                name_or_ticker,
                fetch_limit,
                filter=Filter(must=must_conditions),
            )

            # Re-rank based on market cap using log-scale weight
            reranked_results = self._rerank_by_market_cap(documents_with_score)

            return [
                self._map_document_to_asset(doc)
                for doc, _ in reranked_results[:return_limit]
            ]
        else:
            records, _id = await self.async_client.scroll(
                collection_name=self.configuration["qdrant_collection"],
                scroll_filter=Filter(must=must_conditions),
                limit=return_limit,
                order_by=OrderBy(
                    key="metadata.source.market_cap_usd", direction=Direction.DESC
                ),
            )

            return [self._map_record_to_asset(record) for record in records]

    def _rerank_by_market_cap(
        self,
        documents_with_score: list[tuple[Document, float]],
        similarity_weight: float = 0.6,
    ) -> list[tuple[Document, float]]:
        """
        Re-ranks search results using a weighted combination of similarity and market cap.

        Uses an additive formula: final_score = w * similarity + (1-w) * market_cap_score
        This allows high market cap to overcome moderate similarity differences.

        Args:
            documents_with_score: List of (document, similarity_score) tuples
            similarity_weight: Weight for similarity score (0-1). Market cap weight is 1 - similarity_weight.
                               Default 0.6 means 60% similarity, 40% market cap.

        Returns:
            Reranked list of (document, final_score) tuples sorted by final score
        """
        if not documents_with_score:
            return []

        # Extract market caps for normalization
        market_caps: list[int] = [
            doc.metadata["source"]["market_cap_usd"] for doc, _ in documents_with_score
        ]
        max_market_cap = max(market_caps) if market_caps else 1

        reranked: list[tuple[Document, float]] = []
        for doc, similarity_score in documents_with_score:
            market_cap = doc.metadata["source"]["market_cap_usd"]

            # Square root normalization of market cap (0 to 1 range)
            # sqrt compresses less than log, giving more advantage to high market cap
            if market_cap > 0 and max_market_cap > 0:
                market_cap_score = math.sqrt(market_cap) / math.sqrt(max_market_cap)
            else:
                market_cap_score = 0

            # Weighted combination of similarity and market cap
            market_cap_weight = 1 - similarity_weight
            final_score = (
                similarity_weight * similarity_score
                + market_cap_weight * market_cap_score
            )

            reranked.append((doc, final_score))

        # Sort by final score in descending order
        reranked.sort(key=lambda x: x[1], reverse=True)

        return reranked

    async def get(self, ids: list[str]):
        return [
            self.__map_document_to_similarity_document(doc)
            for doc in await self.qdrant.aget_by_ids(ids)
        ]

    async def get_by_field(self, name: str, value: str) -> list[SimilarityDocument]:
        records: list[Record] = []
        offset = None

        while True:
            points, next_offset = await self.async_client.scroll(
                collection_name=self.configuration["qdrant_collection"],
                scroll_filter=Filter(
                    should=[
                        FieldCondition(
                            key=f"metadata.{name}",
                            match=MatchValue(value=value),
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

    def _map_record_to_asset(self, record: Record) -> Asset:
        if record.payload is None:
            raise InvalidSimilarityDocument(
                f"Record payload is None for record ID {record.id}"
            )
        metadata = cast(dict[str, Any], record.payload["metadata"])

        match metadata["type"]:
            case "token":
                ChildAsset = Token
            case "basket":
                ChildAsset = Basket
            case _:
                raise InvalidSimilarityDocument(metadata["_id"])

        return ChildAsset(
            address=metadata["source"]["address"],
            id=metadata["source"]["id"],
            name=metadata["source"]["name"],
            display_name=metadata["source"]["display_name"],
            ticker=metadata["source"]["ticker"],
            description=metadata["source"]["description"],
            decimals=int(metadata["source"]["decimals"]),
            categories=metadata["source"]["categories"],
            logo_uri=metadata["source"].get("logo_uri"),
        )

    def _map_document_to_asset(self, document: Document) -> Asset:
        metadata = cast(dict[str, Any], document.metadata)

        match metadata["type"]:
            case "token":
                ChildAsset = Token
            case "basket":
                ChildAsset = Basket
            case _:
                raise InvalidSimilarityDocument(metadata["_id"])

        return ChildAsset(
            address=metadata["source"]["address"],
            id=metadata["source"]["id"],
            name=metadata["source"]["name"],
            display_name=metadata["source"]["display_name"],
            ticker=metadata["source"]["ticker"],
            description=metadata["source"]["description"],
            decimals=int(metadata["source"]["decimals"]),
            categories=metadata["source"]["categories"],
            logo_uri=metadata["source"].get("logo_uri"),
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
