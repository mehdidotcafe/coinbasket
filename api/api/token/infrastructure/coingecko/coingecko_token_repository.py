import re
from typing import Any, Literal, TypedDict, cast
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


class GetFromAddressTokenUsdValue(BaseModel):
    usd: float | None = None


class CoinGeckoTokenUsdDateValue(BaseModel):
    usd: str | None = None


class GetFromAddressTokenLinks(BaseModel):
    homepage: list[str] | None = None
    whitepaper: str | None = None


class GetFromAddressTokenMarketData(BaseModel):
    mcap_to_tvl_ratio: float | Literal["-"] | None = None
    fdv_to_tvl_ratio: float | Literal["-"] | None = None
    ath_change_percentage: GetFromAddressTokenUsdValue
    ath_date: CoinGeckoTokenUsdDateValue
    atl_change_percentage: GetFromAddressTokenUsdValue
    atl_date: CoinGeckoTokenUsdDateValue
    market_cap: GetFromAddressTokenUsdValue
    market_cap_rank: int | None = None
    fully_diluted_valuation: GetFromAddressTokenUsdValue
    total_volume: GetFromAddressTokenUsdValue
    price_change_percentage_24h: float | None = None
    price_change_percentage_7d: float | None = None
    price_change_percentage_30d: float | None = None
    price_change_percentage_60d: float | None = None
    price_change_percentage_200d: float | None = None
    price_change_percentage_1y: float | None = None
    total_supply: float | None = None
    max_supply: float | None = None
    circulating_supply: float | None = None
    total_value_locked: GetFromAddressTokenUsdValue | None = None


class GetFromAddressTokenDeveloperData(BaseModel):
    forks: int | None = None
    stars: int | None = None


class GetFromAddressTokenTicker(BaseModel):
    trust_score: str | None = None
    market: dict[str, Any] | None = None
    base: str | None = None
    target: str | None = None
    volume: float | None = None


class GetFromAddressTokenEnText(BaseModel):
    en: str | None = None


class GetFromAddressToken(BaseModel):
    id: str
    name: str
    symbol: str
    categories: list[str]
    localization: GetFromAddressTokenEnText
    description: GetFromAddressTokenEnText
    links: GetFromAddressTokenLinks
    detail_platforms: GetFromAddressTokenDetailPlatforms
    sentiment_votes_up_percentage: float | None = None
    sentiment_votes_down_percentage: float | None = None
    watchlist_portfolio_users: int | None = None
    market_cap_rank: int | None = None
    image: GetFromAddressTokenDetailPlatformImage
    market_data: GetFromAddressTokenMarketData
    developer_data: GetFromAddressTokenDeveloperData
    tickers: list[GetFromAddressTokenTicker]
    platforms: dict[str, str] | None = None
    logoURI: str | None = None


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

    async def get_by_address(
        self, address: str
    ) -> tuple[TokenSimilarity, BaseModel] | None:
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

        return (
            TokenSimilarity(
                id=f"bsc:{address}".lower(),
                name=token.name,
                display_name=self._clean_display_name(token.name),
                ticker=token.symbol.upper(),
                address=address,
                description=token.description.en or "",
                decimals=token.detail_platforms.binance_smart_chain.decimal_place,
                categories=self._make_categories(token.categories),
                logo_uri=f"https://token-registry.s3.amazonaws.com/icons/tokens/bsc/64/{address}.png",
                market_cap_usd=int(token.market_data.market_cap.usd or 0),
                is_canonical=self._is_canonical(token),
                # Override later with real trust score
                trust_score=0,
            ),
            token,
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

    def _make_categories(self, categories: list[str] | None) -> list[str]:
        categories = [cast(AssetCategory, category) for category in categories or []]

        if "Storage" in categories:
            categories.append("DePIN")

        if next(
            (
                category
                for category in categories
                if re.search(r"(?i)\b(Stablecoin)\b", category)
                and category != "Stablecoins"
            ),
            None,
        ):
            categories.append("Stablecoins")

        return list(set(categories))

    def _is_canonical(self, token: GetFromAddressToken) -> int:
        patterns = [
            r"(?i)\b(Binance Pegged|Binance Bridged|Binance-Peg)\b",
        ]

        if token.categories and "Binance Bridged" in token.categories:
            return 1

        for pattern in patterns:
            if re.search(pattern, token.name):
                return 1
        return 0

    def _clean_display_name(self, name: str) -> str:
        display_name = re.sub(
            r"(?i)(\b(Binance Pegged|Wrapped|Binance Bridged|Binance-Peg)\b|\(BNB Smart Chain\))",
            "",
            name,
        ).strip()
        display_name = re.sub(r"\s+", " ", display_name)
        return display_name
