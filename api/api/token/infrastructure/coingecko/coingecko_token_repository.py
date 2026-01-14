import re
from typing import Any, TypedDict, cast
from api.protocol.asset_category import AssetCategory
from api.similarity.asset_similarity import TokenSimilarity
from api.token.token_repository import TokenRepository
from api.protocol.token import Token
from pydantic import BaseModel, Field
from api.shared.http_request.exception.failed_request import FailedRequest
from api.shared.http_request.http_request import HttpRequest


class Configuration(TypedDict):
    coingecko_base_url: str
    coingecko_api_key: str


class GetFromAddressTokenDetailPlatform(BaseModel):
    decimal_place: int
    contract_address: str


class GetFromAddressTokenDetailPlatformImage(BaseModel):
    small: str


class GetFromAddressTokenDetailPlatforms(BaseModel):
    binance_smart_chain: GetFromAddressTokenDetailPlatform = Field(
        alias="binance-smart-chain",
    )

    model_config = {"populate_by_name": True}


class GetFromAddressTokenDetailMarketCap(BaseModel):
    usd: float


class GetFromAddressTokenDetailMarketData(BaseModel):
    market_cap: GetFromAddressTokenDetailMarketCap


class GetFromAddressToken(BaseModel):
    id: str
    symbol: str
    name: str
    detail_platforms: GetFromAddressTokenDetailPlatforms
    categories: list[str]
    description: dict[str, str]
    image: GetFromAddressTokenDetailPlatformImage
    market_data: GetFromAddressTokenDetailMarketData


class CoinGeckoToken(BaseModel):
    chainId: int
    address: str
    name: str
    symbol: str
    decimals: int
    categories: list[str] | None = None
    logoURI: str | None = None

    def to_domain(self) -> Token:
        return Token(
            id=f"bsc:{self.address}".lower(),
            name=self.name,
            display_name=self.name,
            ticker=self.symbol.upper(),
            address=self.address,
            description="",
            decimals=self.decimals,
            categories=[
                cast(AssetCategory, category) for category in self.categories or []
            ],
            logo_uri=self.logoURI.replace("/thumb/", "/small/")
            if self.logoURI
            else None,
        )


class GetAllTokenResponse(BaseModel):
    tokens: list[CoinGeckoToken]


class CoingeckoTokenRepository(TokenRepository):
    def __init__(self, http_request: HttpRequest, config: Configuration):
        self.http_request = http_request
        self.config = config
        self.platform_id = "binance-smart-chain"

    async def get_all_tokens(self) -> list[Token]:
        token_list = await self.http_request.get(
            {
                "url": f"{self.config['coingecko_base_url']}/v3/token_lists/{self.platform_id}/all.json",
                "headers": self._build_headers(),
            },
            GetAllTokenResponse,
        )

        return [token.to_domain() for token in token_list.tokens]

    async def get_by_address(self, address: str) -> TokenSimilarity | None:
        try:
            token = await self.http_request.get(
                {
                    "url": f"{self.config['coingecko_base_url']}/v3/coins/{self.platform_id}/contract/{address}",
                    "headers": self._build_headers(),
                },
                GetFromAddressToken,
            )
        except FailedRequest as e:
            print(f"{__name__} error: {e}")
            if e.status_code == 404:
                return None
            raise e

        return TokenSimilarity(
            id=f"bsc:{address}".lower(),
            name=token.name,
            display_name=self._clean_display_name(token.name),
            ticker=token.symbol.upper(),
            address=address,
            description=token.description["en"],
            decimals=token.detail_platforms.binance_smart_chain.decimal_place,
            categories=[
                cast(AssetCategory, category) for category in token.categories or []
            ],
            logo_uri=token.image.small,
            market_cap_usd=int(token.market_data.market_cap.usd),
        )

    async def get_by_address_raw(self, address: str) -> Any | None:
        try:
            raw_token = await self.http_request.get_raw(
                {
                    "url": f"{self.config['coingecko_base_url']}/v3/coins/{self.platform_id}/contract/{address}",
                    "headers": self._build_headers(),
                },
            )
        except FailedRequest as e:
            print(f"{__name__} error: {e}")
            if e.status_code == 404:
                return None
            raise e

        return raw_token

    def _build_headers(self) -> dict[str, str]:
        headers = {
            "accept": "application/json",
        }

        if "api-pro" in self.config["coingecko_base_url"]:
            headers["x-cg-pro-api-key"] = self.config["coingecko_api_key"]
        else:
            headers["x-cg-demo-api-key"] = self.config["coingecko_api_key"]

        return headers

    def _clean_display_name(self, name: str) -> str:
        """
        Removes 'Binance Pegged' and 'Wrapped' (case-insensitive) from the name and trims/normalizes spaces.
        """
        display_name = re.sub(r"(?i)\b(Binance Pegged|Wrapped)\b", "", name).strip()
        display_name = re.sub(r"\s+", " ", display_name)
        return display_name
