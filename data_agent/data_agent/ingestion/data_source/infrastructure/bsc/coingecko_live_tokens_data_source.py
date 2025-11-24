from pydantic import BaseModel

from data_agent.ingestion.id.id_generator import IdGenerator
from data_agent.similarity.similarity_document import SimilarityDocument
from data_agent.ingestion.data_source.data_source import DataSource
from shared.http_request.http_request import HttpRequest
from protocol.token import Token
from typing import TypedDict


class Configuration(TypedDict):
    coingecko_base_url: str
    coingecko_api_key: str


class CoinListToken(BaseModel):
    chainId: int
    address: str
    name: str
    symbol: str
    decimals: int
    logoURI: str | None = None


class CoinListResponse(BaseModel):
    tokens: list[CoinListToken]


class CoinDetailPlatform(BaseModel):
    decimal_place: int | None = None
    contract_address: str | None = None


class CoinDetailResponse(BaseModel):
    id: str
    symbol: str
    name: str
    detail_platforms: dict[str, CoinDetailPlatform] | None = None


class CoingeckoLiveTokenListDataSource(DataSource):
    """Dynamic CoinGecko token datasource.

    Step 1: Fetch global coin list with platform mappings and filter for Binance Smart Chain ("binance-smart-chain").
    Step 2: Fetch detail per filtered coin to enrich with decimal precision (future: description, metadata).

    Scope (current): Provide Token similarity documents with id, name, display_name, ticker, address.
    Future (not implemented): Store description and decimals in model metadata once domain supports it.
    """

    def __init__(
        self,
        http_request: HttpRequest,
        id_generator: IdGenerator,
        config: Configuration,
    ):
        self.bsc_id = "binance-smart-chain"
        self.config = config
        self.list_url = (
            f"{self.config['coingecko_base_url']}/v3/token_lists/{self.bsc_id}/all.json"
        )
        self.http_request = http_request
        self.id_generator = id_generator

        self.headers = {
            "accept": "application/json",
        }

        if "api-pro" in self.config["coingecko_base_url"]:
            self.headers["x-cg-pro-api-key"] = self.config["coingecko_api_key"]
        else:
            self.headers["x-cg-demo-api-key"] = self.config["coingecko_api_key"]

    async def get(self) -> list[SimilarityDocument]:
        token_list = await self.http_request.get(
            {
                "url": self.list_url,
                "headers": self.headers,
            },
            CoinListResponse,
        )

        documents: list[SimilarityDocument] = []

        for token in token_list.tokens:
            token = Token(
                id=f"bsc:{token.address}",
                name=token.name,
                display_name=token.name,
                ticker=token.symbol,
                address=token.address,
            )

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
        return documents

    async def _fetch_detail(self, contract_address: str) -> CoinDetailResponse:
        return await self.http_request.get(
            {
                "url": f"{self.config['coingecko_base_url']}/v3/coins/{self.bsc_id}/contract/{contract_address}",
                "headers": self.headers,
            },
            CoinDetailResponse,
        )

    def version(self) -> int:
        return 4

    def _generate_id(self, token: Token) -> str:
        return self.id_generator.generate_id(token.address[2:])
