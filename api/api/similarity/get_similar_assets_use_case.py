from typing import Any, Literal
from api.protocol.basket import Basket
from api.protocol.token import Token
from api.similarity.exception.invalid_similarity_document import (
    InvalidSimilarityDocument,
)
from api.similarity.similarity_document import SimilarityDocument
from api.similarity.similarity_storage.similarity_storage import (
    SimilarityStorage,
)
from api.protocol.asset import Asset


class GetSimilarAssetsUseCase:
    def __init__(self, storage: SimilarityStorage):
        self.storage = storage

    async def execute(
        self, query: str, type: Literal["BASKET", "TOKEN"] | None
    ) -> list[Asset]:
        documents = await self.storage.similarity_search(
            query, {"type": type.lower() if type else None}
        )

        return [self._map_similarity_document_to_asset(doc) for doc in documents]

    def _map_similarity_document_to_asset(self, document: SimilarityDocument) -> Asset:
        metadata = document.metadata

        if not metadata:
            raise InvalidSimilarityDocument(document.id)

        return self._map_similarity_document_metadata_to_asset(metadata["source"])

    def _map_similarity_document_metadata_to_asset(self, metadata: Any):
        match metadata["type"]:
            case "TOKEN":
                ChildAsset = Token
            case "BASKET":
                ChildAsset = Basket
            case _:
                raise InvalidSimilarityDocument(metadata["id"])

        return ChildAsset(
            address=metadata["address"],
            id=metadata["id"],
            name=metadata["name"],
            display_name=metadata["display_name"],
            ticker=metadata["ticker"],
            description=metadata["description"],
            decimals=int(metadata["decimals"]),
            categories=metadata["categories"],
            logo_uri=metadata.get("logo_uri"),
        )
