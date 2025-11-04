from decimal import Decimal
from typing import Any
from data_agent.similarity.exception.invalid_similarity_document import (
    InvalidSimilarityDocument,
)
from data_agent.similarity.similarity_document import SimilarityDocument
from data_agent.similarity.similarity_storage.similarity_storage import (
    SimilarityStorage,
)
from protocol.basket import Basket
from protocol.token import Token
from protocol.asset import Asset


class GetAssetByIdUseCase:
    def __init__(self, asset_repository: SimilarityStorage):
        self.asset_repository = asset_repository

    async def execute(self, id: str) -> Asset | None:
        similarity_documents = await self.asset_repository.get_by_field(
            name="source.id",
            value=id.lower(),
        )

        if not similarity_documents:
            return None

        similarity_document = similarity_documents[0]

        if not similarity_document.metadata:
            raise InvalidSimilarityDocument(similarity_document.id)

        return (
            self._map_similarity_document_to_basket(similarity_document)
            if similarity_document.metadata["type"] == "basket"
            else self._map_similarity_document_metadata_to_token(
                similarity_document.metadata["source"]
            )
        )

    def _map_similarity_document_to_basket(
        self, document: SimilarityDocument
    ) -> Basket:
        metadata = document.metadata

        if not metadata or metadata["type"] != "basket":
            raise InvalidSimilarityDocument(document.id)

        return Basket(
            id=metadata["source"]["id"],
            display_name=metadata["source"]["display_name"],
            name=metadata["source"]["name"],
            ticker=metadata["source"]["ticker"],
            description=metadata["source"]["description"],
            denomination=Decimal(metadata["source"]["denomination"]),
            tokens=[
                self._map_similarity_document_metadata_to_token(token)
                for token in metadata["source"]["tokens"]
            ],
        )

    def _map_similarity_document_metadata_to_token(self, metadata: dict[str, Any]):
        return Token(
            address=metadata["address"],
            id=metadata["id"],
            name=metadata["name"],
            display_name=metadata["display_name"],
            ticker=metadata["ticker"],
        )
