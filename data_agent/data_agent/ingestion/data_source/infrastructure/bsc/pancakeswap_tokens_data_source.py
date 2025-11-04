from pydantic import BaseModel
import re
from data_agent.ingestion.id.id_generator import IdGenerator
from data_agent.similarity.similarity_document import SimilarityDocument
from data_agent.ingestion.data_source.data_source import DataSource
from shared.http_request.http_request import HttpRequest

from protocol.token import Token


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

    async def get(self) -> list[SimilarityDocument]:
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
            self.__map_pancakeswap_token_to_similarity_document(token)
            for token in tokens.tokens
        ]

    def version(self):
        return 3

    def __map_pancakeswap_token_to_similarity_document(
        self, pancakeswap_token: PancakeswapToken
    ) -> SimilarityDocument:
        """
        Maps a PancakeswapToken to a Token.
        """
        token = Token(
            id=f"bsc:{pancakeswap_token.address}",
            name=pancakeswap_token.name,
            display_name=self.__clean_display_name(pancakeswap_token.name),
            ticker=pancakeswap_token.symbol,
            address=pancakeswap_token.address,
        )

        return SimilarityDocument(
            id=self.__generate_id(token),
            page_content=str(token),
            metadata={
                "source": token.to_dict(),
                "type": "token",
                "version": self.version(),
            },
        )

    def __generate_id(self, token: Token) -> str:
        """
        Generates a unique ID (UUID) for the token based on its address.
        """
        return self.id_generator.generate_id(token.address[2:])
