from api.ingestion.data_source.data_source import DataSource
from api.shared.id_generator.id_generator import IdGenerator
from api.similarity.asset_similarity import AssetSimilarity, TokenSimilarity


class NativeBnbDataSource(DataSource):
    def __init__(self, id_generator: IdGenerator):
        self.id_generator = id_generator
        self.token = TokenSimilarity(
            id="bsc:0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
            name="Binance Coin",
            display_name="Binance Coin",
            ticker="BNB",
            address="0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
            description='BNB is the native coin of the BNB Chain ecosystem, essential for powering its multifaceted Web3 environment. It supports transactions on the BNB Smart Chain (BSC), the opBNB L2s, and BNB Greenfield. Besides transaction fees, BNB serves as a governance token, granting holders the ability to participate in the BNB Chain’s decentralized on-chain governance. Additionally, BNB functions as a strategic reserve asset and plays a critical role in the BNB Executive Total Value Locked (TVL) campaign, driving ecosystem growth and incentivizing adoption. Originally launched in 2017 as Binance’s exchange token, BNB was designed to offer trading fee discounts and other utilities within the Binance platform. It later evolved into the foundational asset of a much broader ecosystem. Following its mainnet launch on April 18, 2019, BNB transitioned from the Ethereum Network to BNB Chain. "Build and Build" is the philosophy behind BNB, reflecting its role in fostering development within the ecosystem.',
            decimals=18,
            categories=[
                "Crypto-Backed Tokens",
                "BNB Chain Ecosystem",
                "Wrapped-Tokens",
                "Native Token",
                "Coinbasket Selection",
            ],
            logo_uri="https://token-registry.s3.amazonaws.com/icons/tokens/bsc/64/0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c.png",
            trust_score=100,
            is_canonical=1,
            market_cap_usd=85763281181,
        )

    async def get(self) -> list[AssetSimilarity]:
        return [self.token]

    def version(self) -> int:
        return 1
