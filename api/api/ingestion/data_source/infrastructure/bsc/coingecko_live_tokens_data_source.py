import asyncio
from api.similarity.asset_similarity import AssetSimilarity
from api.similarity.trust_scorer.asset_trust_scorer_strategy import (
    AssetTrustScorerStrategy,
)
from api.token.infrastructure.coingecko.coingecko_token_repository import (
    CoingeckoTokenRepository,
)

from api.shared.id_generator.id_generator import IdGenerator
from api.ingestion.data_source.data_source import DataSource


class CoingeckoLiveTokenListDataSource(DataSource):
    """Enhanced CoinGecko token datasource with metadata enrichment."""

    blacklist_tokens = ["0x2f8a339b5889ffac4c5a956787cda593b3c36867"]

    def __init__(
        self,
        id_generator: IdGenerator,
        token_repository: CoingeckoTokenRepository,
        asset_trust_scorer_strategy: AssetTrustScorerStrategy,
    ):
        self.id_generator = id_generator
        self.token_repository = token_repository
        self.asset_trust_scorer_strategy = asset_trust_scorer_strategy

    async def get(self) -> list[AssetSimilarity]:
        tokens = await self.token_repository.get_all_tokens()
        tokens_similarity: list[AssetSimilarity] = []

        for coingecko_token in tokens:
            if coingecko_token.address.lower() in self.blacklist_tokens:
                continue

            result = await self.token_repository.get_by_address(coingecko_token.address)

            if result is None:
                continue

            token = result[0]

            token.trust_score = await self.asset_trust_scorer_strategy.score(
                result[1].model_dump()
            )

            tokens_similarity.append(token)

            # Coingecko DEMO Rate Limit is 30 calls per minute
            await asyncio.sleep(2)

        return tokens_similarity

    def version(self) -> int:
        return 7
