import asyncio
from typing import Any, Literal, TypedDict
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
        self.client.create_payload_index(
            collection_name=self.configuration["qdrant_collection"],
            field_name="metadata.source.is_canonical",
            field_schema=PayloadSchemaType.INTEGER,
        )
        self.client.create_payload_index(
            collection_name=self.configuration["qdrant_collection"],
            field_name="metadata.source.id",
            field_schema=PayloadSchemaType.KEYWORD,
        )
        self.client.create_payload_index(
            collection_name=self.configuration["qdrant_collection"],
            field_name="metadata.type",
            field_schema=PayloadSchemaType.KEYWORD,
        )
        self.client.create_payload_index(
            collection_name=self.configuration["qdrant_collection"],
            field_name="metadata.categories",
            field_schema=PayloadSchemaType.KEYWORD,
        )
        self.qdrant = self.qdrant_vector_store(
            client=self.client,
            collection_name=self.configuration["qdrant_collection"],
            embedding=self.embeddings,
        )

    # TODO: Use qdrant native reranking
    # https://qdrant.tech/documentation/concepts/hybrid-queries/
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

        if type:
            must_conditions.append(
                FieldCondition(
                    key="metadata.type",
                    match=MatchValue(value=type.lower()),
                )
            )

        reranked_raw_assets: list[tuple[dict[str, Any], float]] = []

        # Address exact match has highest priority
        if name_or_ticker and name_or_ticker.startswith("0x"):
            results, _ = await self.async_client.scroll(
                collection_name=self.configuration["qdrant_collection"],
                scroll_filter=Filter(
                    must=[
                        *must_conditions,
                        FieldCondition(
                            key="metadata.source.address",
                            match=MatchValue(value=name_or_ticker.lower()),
                        ),
                    ]
                ),
                limit=fetch_limit,
            )

            reranked_raw_assets = self._rerank_results(
                [
                    (record.payload["metadata"], 1.0)
                    for record in results
                    if record.payload
                ],
            )

        elif name_or_ticker:
            documents_with_score = await self.qdrant.asimilarity_search_with_score(
                name_or_ticker,
                fetch_limit,
                filter=Filter(must=must_conditions),
            )

            # Re-rank based on market cap, similarity, and canonical status
            reranked_raw_assets = self._rerank_results(
                [
                    (doc.metadata, score)
                    for doc, score in documents_with_score
                    if doc.metadata
                ]
            )

        else:
            if categories:
                must_conditions.extend(
                    FieldCondition(
                        key="metadata.source.categories",
                        match=MatchValue(value=category),
                    )
                    for category in categories
                )

            results = await asyncio.gather(
                *[
                    # Fetch non-canonical assets ordered by market cap descending
                    self.async_client.scroll(
                        collection_name=self.configuration["qdrant_collection"],
                        scroll_filter=Filter(
                            must=[
                                *must_conditions,
                                FieldCondition(
                                    key="metadata.source.is_canonical",
                                    match=MatchValue(value=0),
                                ),
                            ]
                        ),
                        limit=fetch_limit,
                        order_by=OrderBy(
                            key="metadata.source.market_cap_usd",
                            direction=Direction.DESC,
                        ),
                    ),
                    # Fetch canonical assets without specific ordering, canonical assets often have zero market cap provided
                    self.async_client.scroll(
                        collection_name=self.configuration["qdrant_collection"],
                        scroll_filter=Filter(
                            must=[
                                *must_conditions,
                                FieldCondition(
                                    key="metadata.source.is_canonical",
                                    match=MatchValue(value=1),
                                ),
                            ]
                        ),
                        limit=fetch_limit,
                    ),
                ]
            )

            records = results[0][0] + results[1][0]

            reranked_raw_assets = self._rerank_results(
                [
                    (record.payload["metadata"], 0)
                    for record in records
                    if record.payload
                ],
            )

        for asset, score in reranked_raw_assets:
            print(
                f"Record Token: {asset['source']['name']}, Score: {score}, Market Cap: {asset['source']['market_cap_usd']}"
            )

        return [
            self._map_raw_asset_to_asset(asset)
            for (asset, _) in reranked_raw_assets[:return_limit]
        ]

    def _rerank_results(
        self,
        documents_with_score: list[tuple[dict[str, Any], float]],
        similarity_weight: float = 0.55,
        market_cap_weight: float = 0.35,
        canonical_weight: float = 0.10,
    ) -> list[tuple[dict[str, Any], float]]:
        """
        Re-ranks search results using a weighted combination of similarity, market cap, and canonical status.

        Uses an additive formula:
            final_score = similarity_weight * similarity
                        + market_cap_weight * market_cap_score
                        + canonical_weight * canonical_score

        Canonical tokens with market_cap = 0 receive a neutral market_cap_score (0.5)
        to avoid being penalized by missing/erroneous provider data.

        Args:
            documents_with_score: List of (document, similarity_score) tuples
            similarity_weight: Weight for similarity score. Default 0.55.
            market_cap_weight: Weight for market cap score. Default 0.35.
            canonical_weight: Weight for canonical status. Default 0.10.

        Returns:
            Reranked list of (document, final_score) tuples sorted by final score
        """
        if not documents_with_score:
            return []

        # Extract market caps for normalization
        market_caps: list[int] = [
            doc["source"]["market_cap_usd"] for doc, _ in documents_with_score
        ]
        max_market_cap = max(market_caps) if market_caps else 1

        reranked: list[tuple[dict[str, Any], float]] = []
        for doc, similarity_score in documents_with_score:
            market_cap = doc["source"]["market_cap_usd"]
            is_canonical = doc["source"]["is_canonical"]

            # Market cap score with rescue for canonical tokens
            if market_cap > 0 and max_market_cap > 0:
                market_cap_score = math.sqrt(market_cap) / math.sqrt(max_market_cap)
            elif market_cap == 0 and is_canonical:
                # Rescue canonical tokens with missing/erroneous market cap data
                market_cap_score = 0.5
            else:
                market_cap_score = 0

            # Canonical score
            canonical_score = 1.0 if is_canonical else 0.0

            # Three-factor weighted combination
            final_score = (
                similarity_weight * similarity_score
                + market_cap_weight * market_cap_score
                + canonical_weight * canonical_score
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

    # TODO: Rename get by id
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

    def _map_raw_asset_to_asset(self, asset: dict[str, Any]) -> Asset:
        match asset["type"]:
            case "token":
                ChildAsset = Token
            case "basket":
                ChildAsset = Basket
            case _:
                raise InvalidSimilarityDocument(asset["_id"])

        return ChildAsset(
            address=asset["source"]["address"],
            id=asset["source"]["id"],
            name=asset["source"]["name"],
            display_name=asset["source"]["display_name"],
            ticker=asset["source"]["ticker"],
            description=asset["source"]["description"],
            decimals=int(asset["source"]["decimals"]),
            categories=asset["source"]["categories"],
            trust_score=int(asset["source"]["trust_score"]),
            logo_uri=asset["source"].get("logo_uri"),
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
