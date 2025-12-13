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


class GetAllBasketsUseCase:
    def __init__(self, basket_repository: SimilarityStorage):
        self.basket_repository = basket_repository

    async def execute(self) -> list[Basket]:
        similarity_documents = await self.basket_repository.get_by_field(
            name="type",
            value="basket",
        )

        baskets = [
            self._map_similarity_document_to_basket(doc) for doc in similarity_documents
        ]

        return sorted(baskets, key=lambda b: b.display_name)

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
            description=metadata["description"],
            decimals=int(metadata["decimals"]),
            categories=metadata["categories"],
            logo_uri=metadata.get("logo_uri"),
        )
