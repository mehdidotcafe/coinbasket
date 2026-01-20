from api.similarity.exception.invalid_similarity_document import (
    InvalidSimilarityDocument,
)
from api.similarity.similarity_document import SimilarityDocument
from api.similarity.asset_similarity_repository import (
    AssetSimilarityRepository,
)
from api.protocol.basket import Basket


class GetAllBasketsUseCase:
    def __init__(self, basket_repository: AssetSimilarityRepository):
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
            address=metadata["source"]["address"],
            decimals=int(metadata["source"]["decimals"]),
            categories=metadata["source"]["categories"],
            logo_uri=metadata["source"].get("logo_uri"),
        )
