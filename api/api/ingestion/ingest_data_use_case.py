from typing import Union

from api.shared.id_generator.id_generator import IdGenerator
from api.similarity.asset_similarity import AssetSimilarity, TokenSimilarity
from api.similarity.similarity_document import SimilarityDocument
from api.similarity.asset_similarity_repository import (
    AssetSimilarityRepository,
)
from api.ingestion.data_source.data_source import DataSource
from api.protocol.basket import Basket
from api.protocol.token import Token

type Data = Union[list[Token], list[Basket]]


class IngestDataUseCase:
    def __init__(
        self,
        similarity_storage: AssetSimilarityRepository,
        id_generator: IdGenerator,
        data_sources: list[DataSource],
    ):
        self.similarity_storage = similarity_storage
        self.id_generator = id_generator
        self.data_sources = data_sources

    # TODO: Current use case does NOT remove documents from the storage if not in the data source (use qdrant `scroll` API)
    async def execute(self):
        for data_source in self.data_sources:
            try:
                assets = await data_source.get()

                assets_with_ids = [
                    (asset, self._generate_id(asset)) for asset in assets
                ]

                stored_documents = await self.similarity_storage.get(
                    [asset_id for _, asset_id in assets_with_ids]
                )

                assets_with_ids_to_update = self.filter_assets_to_update(
                    assets_with_ids, stored_documents, data_source.version()
                )

                if (len(assets_with_ids_to_update)) > 0:
                    print(
                        f"Updating {data_source.__class__.__name__} assets in the storage."
                    )
                    self.similarity_storage.set(
                        [
                            SimilarityDocument(
                                id=asset_id,
                                page_content=asset.to_document(),
                                metadata={
                                    "source": asset.to_dict(),
                                    "type": "token"
                                    if isinstance(asset, TokenSimilarity)
                                    else "basket",
                                    "version": data_source.version(),
                                },
                            )
                            for asset, asset_id in assets_with_ids_to_update
                        ]
                    )
                else:
                    print(f"No update for datasource {data_source.__class__.__name__}.")
            except Exception as e:
                print(f"Error for datasource {data_source.__class__.__name__}: {e}")

    def filter_assets_to_update(
        self,
        assets: list[tuple[AssetSimilarity, str]],
        stored_documents: list[SimilarityDocument],
        data_source_version: int,
    ) -> list[tuple[AssetSimilarity, str]]:
        return [
            (asset, id)
            for asset, id in assets
            if id
            not in [
                stored_doc.id
                for stored_doc in stored_documents
                if stored_doc.id == id
                and stored_doc.metadata["version"] >= data_source_version
            ]
        ]

    def _generate_id(self, asset: AssetSimilarity) -> str:
        return self.id_generator.generate_id(asset.address[2:])
