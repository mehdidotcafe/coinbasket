from api.ingestion.data_source.data_source import DataSource
from api.shared.id_generator.id_generator import IdGenerator
from api.similarity.asset_similarity import AssetSimilarity, BasketSimilarity


class CmcTop20BasketDataSource(DataSource):
    def __init__(self, id_generator: IdGenerator):
        self.id_generator = id_generator
        self.id = "0x2f8A339B5889FfaC4c5A956787cdA593b3c36867".lower()
        self.basket = BasketSimilarity(
            id=f"bsc:{self.id}",
            name="CoinMarketCap 20 Index DTF",
            display_name="CoinMarketCap 20",
            ticker="CMC20",
            description="The CoinMarketCap 20 Index DTF (CMC20) is a liquid index token powered by Reserve that tracks the CoinMarketCap 20 Index. The CMC20 Index is a benchmark designed to measure the performance of the top 20 cryptocurrency projects by market capitalization, as ranked by CoinMarketCap. It excludes stablecoins (i.e. USDT), tokens that are pegged to other crypto assets (i.e. WBTC or stETH), and assets with limited investability (e.g. potential litigation risk, or limited circulating liquidity). The index represents the broader cryptocurrency market while providing insight into the performance of a diverse set of digital assets.",
            address=self.id,
            logo_uri="https://token-registry.s3.amazonaws.com/icons/tokens/bsc/64/0x2f8a339b5889ffac4c5a956787cda593b3c36867.png",
            categories=["BNB Chain Ecosystem", "DTF", "Basket"],
            decimals=18,
            market_cap_usd=6_773_392,
            is_canonical=1,
        )

    async def get(self) -> list[AssetSimilarity]:
        return [self.basket]

    def version(self) -> int:
        return 1
