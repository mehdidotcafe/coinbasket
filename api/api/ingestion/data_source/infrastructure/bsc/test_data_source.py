from api.protocol.asset import Asset
from api.shared.id_generator.id_generator import IdGenerator
from api.similarity.similarity_document import SimilarityDocument
from api.ingestion.data_source.data_source import DataSource
from api.protocol.fixture.token import (
    wbnb_token,
    eth_token,
    btc_token,
    sol_token,
    usdt_token,
    shib_token,
    cake_token,
)
from api.protocol.fixture.basket import (
    cmc20_basket,
)


class TestDataSource(DataSource):
    def __init__(
        self,
        id_generator: IdGenerator,
    ):
        self.id_generator = id_generator

    async def get(self) -> list[SimilarityDocument]:
        tokens = [
            wbnb_token,
            eth_token,
            btc_token,
            sol_token,
            usdt_token,
            shib_token,
            cake_token,
        ]
        baskets = [cmc20_basket]
        documents: list[SimilarityDocument] = []

        for asset in tokens:
            documents.append(
                SimilarityDocument(
                    id=self._generate_id(asset),
                    page_content=str(asset),
                    metadata={
                        "source": asset.to_dict(),
                        "type": "token",
                        "version": self.version(),
                    },
                )
            )
        for asset in baskets:
            documents.append(
                SimilarityDocument(
                    id=self._generate_id(asset),
                    page_content=str(asset),
                    metadata={
                        "source": asset.to_dict(),
                        "type": "basket",
                        "version": self.version(),
                    },
                )
            )

        return documents

    def version(self) -> int:
        return 1

    def _generate_id(self, asset: Asset) -> str:
        return self.id_generator.generate_id(asset.address[2:])
