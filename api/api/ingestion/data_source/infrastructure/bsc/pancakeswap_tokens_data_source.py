from pydantic import BaseModel
import re
from api.shared.id_generator.id_generator import IdGenerator
from api.ingestion.data_source.data_source import DataSource
from api.shared.http_request.http_request import HttpRequest
from api.similarity.asset_similarity import AssetSimilarity, TokenSimilarity


class PancakeswapToken(BaseModel):
    chainId: int
    address: str
    name: str
    symbol: str
    decimals: int
    logoURI: str


class Response(BaseModel):
    tokens: list[PancakeswapToken]


class PancakeswapTokenListDataSource(DataSource):
    def __init__(self, http_request: HttpRequest, id_generator: IdGenerator):
        self.url = "https://tokens.pancakeswap.finance/pancakeswap-extended.json"
        self.http_request = http_request
        self.id_generator = id_generator
        self.headers = {
            "accept": "application/json",
        }

    def __clean_display_name(self, name: str) -> str:
        """
        Removes 'Binance Pegged' and 'Wrapped' (case-insensitive) from the name and trims/normalizes spaces.
        """
        display_name = re.sub(r"(?i)\b(Binance Pegged|Wrapped)\b", "", name).strip()
        display_name = re.sub(r"\s+", " ", display_name)
        return display_name

    async def get(self) -> list[AssetSimilarity]:
        """
        Fetches the token list from the Pancakeswap API.
        """
        tokens = await self.http_request.get(
            {
                "url": self.url,
                "headers": self.headers,
            },
            Response,
        )

        return [
            self.__map_pancakeswap_token_to_token_similarity(token)
            for token in tokens.tokens
        ]

    def version(self):
        return 4

    def __map_pancakeswap_token_to_token_similarity(
        self, pancakeswap_token: PancakeswapToken
    ) -> AssetSimilarity:
        """
        Maps a PancakeswapToken to a TokenSimilarity.
        """
        return TokenSimilarity(
            id=f"bsc:{pancakeswap_token.address}",
            name=pancakeswap_token.name,
            display_name=self.__clean_display_name(pancakeswap_token.name),
            ticker=pancakeswap_token.symbol.upper(),
            address=pancakeswap_token.address,
            categories=[],
            description="",
            decimals=pancakeswap_token.decimals,
            logo_uri=f"https://token-registry.s3.amazonaws.com/icons/tokens/bsc/64/{pancakeswap_token.address}.png",
            market_cap_usd=0,
            is_canonical=0,
        )
