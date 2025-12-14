from api.token.infrastructure.coingecko.coingecko_token_repository import (
    CoingeckoTokenRepository,
)

from shared.id_generator.id_generator import IdGenerator
from api.similarity.similarity_document import SimilarityDocument
from api.ingestion.data_source.data_source import DataSource
from protocol.token import Token


class CoingeckoLiveTokenListDataSource(DataSource):
    """Enhanced CoinGecko token datasource with metadata enrichment."""

    def __init__(
        self,
        id_generator: IdGenerator,
        token_repository: CoingeckoTokenRepository,
    ):
        self.id_generator = id_generator
        self.token_repository = token_repository

    async def get(self) -> list[SimilarityDocument]:
        tokens = await self.token_repository.get_all_tokens()
        documents: list[SimilarityDocument] = []

        for coingecko_token in tokens:
            documents.append(
                SimilarityDocument(
                    id=self._generate_id(coingecko_token),
                    page_content=str(coingecko_token),
                    metadata={
                        "source": coingecko_token.to_dict(),
                        "type": "token",
                        "version": self.version(),
                    },
                )
            )
        return documents

    def version(self) -> int:
        return 5

    def _generate_id(self, token: Token) -> str:
        return self.id_generator.generate_id(token.address[2:])
