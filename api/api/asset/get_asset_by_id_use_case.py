from typing import Any
from api.chain.chain import Chain
from api.similarity.exception.invalid_similarity_document import (
    InvalidSimilarityDocument,
)
from api.similarity.asset_similarity_repository import (
    AssetSimilarityRepository,
)
from api.protocol.basket import Basket
from api.protocol.token import Token
from api.protocol.asset import Asset


class GetAssetByIdUseCase:
    def __init__(self, asset_repository: AssetSimilarityRepository, chain: Chain):
        self.asset_repository = asset_repository
        self.chain = chain

    async def execute(self, id: str) -> Asset | None:
        base_token = self.chain.get_base_token()
        if base_token.id.lower() == id.lower():
            return base_token

        similarity_documents = await self.asset_repository.get_by_field(
            name="source.id",
            value=id.lower(),
        )

        if not similarity_documents:
            return None

        similarity_document = similarity_documents[0]

        if not similarity_document.metadata:
            raise InvalidSimilarityDocument(similarity_document.id)

        return self._map_similarity_document_metadata_to_asset(
            similarity_document.metadata
        )

    def _map_similarity_document_metadata_to_asset(self, document_metadata: Any):
        ChildAsset = Token if document_metadata["type"] == "token" else Basket

        return ChildAsset(
            address=document_metadata["source"]["address"],
            id=document_metadata["source"]["id"],
            name=document_metadata["source"]["name"],
            display_name=document_metadata["source"]["display_name"],
            ticker=document_metadata["source"]["ticker"],
            description=document_metadata["source"]["description"],
            decimals=int(document_metadata["source"]["decimals"]),
            categories=document_metadata["source"]["categories"],
            trust_score=int(document_metadata["source"]["trust_score"]),
            logo_uri=document_metadata["source"].get("logo_uri"),
        )
