from api.shared.id_generator.id_generator import IdGenerator
from api.similarity.similarity_document import SimilarityDocument
from api.ingestion.data_source.data_source import DataSource
from api.protocol.token import Token
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
    big4_basket,
    memecoinmania_basket,
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
        baskets = [
            ("2bb6425b-a9ee-4292-89c8-c1f0c7a5cb70", big4_basket),
            ("c0e724d3-c4d0-4bd0-973d-edd3907ecf51", memecoinmania_basket),
        ]
        documents: list[SimilarityDocument] = []

        for token in tokens:
            documents.append(
                SimilarityDocument(
                    id=self._generate_id(token),
                    page_content=str(token),
                    metadata={
                        "source": token.to_dict(),
                        "type": "token",
                        "version": self.version(),
                    },
                )
            )
        for basket_id, basket in baskets:
            documents.append(
                SimilarityDocument(
                    id=basket_id,
                    page_content=str(basket),
                    metadata={
                        "source": basket.to_dict(),
                        "type": "basket",
                        "version": self.version(),
                    },
                )
            )
        return documents

    def version(self) -> int:
        return 1

    def _generate_id(self, token: Token) -> str:
        return self.id_generator.generate_id(token.address[2:])
