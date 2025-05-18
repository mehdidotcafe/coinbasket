from dataclasses import asdict
import hashlib
from typing import TypedDict
import uuid

from data_agent.similarity.similarity_document import SimilarityDocument
from data_agent.ingestion.data_source.data_source import DataSource
from data_agent.http_request.http_request import HttpRequest

from protocol.token import Token


class CoingeckoToken(TypedDict):
    chainId: int
    address: str
    name: str
    symbol: str
    decimals: int
    logoURI: str


class Response(TypedDict):
    tokens: list[CoingeckoToken]


class CoingeckoTokenListDataSource(DataSource):
    def __init__(self, http_request: HttpRequest[Response]):
        self.url = "https://tokens.coingecko.com/binance-smart-chain/all.json"
        self.http_request = http_request
        self.headers = {
            "accept": "application/json",
        }

    def get(self) -> list[SimilarityDocument]:
        """
        Fetches the token list from the CoinGecko API.
        """
        tokens = self.http_request.get(
            {
                "url": self.url,
                "headers": self.headers,
            }
        )

        return [
            self.__map_coingecko_token_to_similarity_document(token)
            for token in tokens["tokens"]
        ]

    def version(self):
        return 1

    def __map_coingecko_token_to_similarity_document(
        self, coingecko_token: CoingeckoToken
    ) -> SimilarityDocument:
        """
        Maps a CoingeckoToken to a Token.
        """
        token = Token(
            name=coingecko_token["name"],
            display_name=coingecko_token["name"],
            ticker=coingecko_token["symbol"],
            address=coingecko_token["address"],
        )

        return SimilarityDocument(
            id=self.__generate_id(token),
            page_content=token.__str__(),
            metadata={
                "source": asdict(token),
                "type": "token",
                "version": self.version(),
            },
        )

    def __generate_id(self, token: Token) -> str:
        """
        Generates a unique ID (UUID) for the token based on its address.
        """
        hash_bytes = hashlib.sha256(token.address[2:].encode()).digest()

        return str(uuid.UUID(bytes=hash_bytes[:16]))
