from api.protocol.asset import Asset
from api.protocol.basket import Basket
from api.protocol.token import Token
from api.shared.id_generator.id_generator import IdGenerator
from api.similarity.asset_similarity import (
    AssetSimilarity,
    BasketSimilarity,
    TokenSimilarity,
)
from api.ingestion.data_source.data_source import DataSource
from api.protocol.fixture.token import (
    wbnb_token,
    eth_token,
    btc_token,
    sol_token,
    usdt_token,
    shib_token,
    cake_token,
    xrp_token,
)
from api.protocol.fixture.basket import (
    cmc20_basket,
    test_basket,
)


class TestDataSource(DataSource):
    def __init__(
        self,
        id_generator: IdGenerator,
    ):
        self.id_generator = id_generator

    async def get(self) -> list[AssetSimilarity]:
        tokens = [
            self._map_token_to_token_similarity(token, 1_000_000_000)
            for token in [
                wbnb_token,
                eth_token,
                btc_token,
                sol_token,
                usdt_token,
                shib_token,
                cake_token,
                xrp_token,
            ]
        ]
        baskets = [
            self._map_basket_to_basket_similarity(cmc20_basket, 5_000_000_000),
            self._map_basket_to_basket_similarity(test_basket, 1_000_000_000),
        ]

        return tokens + baskets

    def version(self) -> int:
        return 1

    def _generate_id(self, asset: Asset) -> str:
        return self.id_generator.generate_id(asset.address[2:])

    def _map_token_to_token_similarity(
        self, token: Token, market_cap_usd: int
    ) -> TokenSimilarity:
        return TokenSimilarity(
            address=token.address,
            id=token.id,
            name=token.name,
            display_name=token.display_name,
            ticker=token.ticker,
            description=token.description,
            decimals=token.decimals,
            categories=token.categories,
            logo_uri=token.logo_uri,
            market_cap_usd=market_cap_usd,
            is_canonical=1,
            trust_score=100,
        )

    def _map_basket_to_basket_similarity(
        self, basket: Basket, market_cap_usd: int
    ) -> BasketSimilarity:
        return BasketSimilarity(
            address=basket.address,
            id=basket.id,
            name=basket.name,
            display_name=basket.display_name,
            ticker=basket.ticker,
            description=basket.description,
            decimals=basket.decimals,
            categories=basket.categories,
            logo_uri=basket.logo_uri,
            market_cap_usd=market_cap_usd,
            is_canonical=1,
            trust_score=100,
        )
