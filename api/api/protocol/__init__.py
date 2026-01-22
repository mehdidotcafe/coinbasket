from typing import Literal
from api.protocol.basket import Basket
from api.protocol.token import Token
from pydantic import BaseModel


class TokenResponse(BaseModel):
    id: str
    name: str
    display_name: str
    ticker: str
    address: str
    description: str
    decimals: int
    categories: list[str]
    trust_score: int
    type: Literal["TOKEN"]
    logo_uri: str | None = None

    @staticmethod
    def from_domain(token: Token) -> "TokenResponse":
        """Convert the domain Token to a TokenResponse."""
        return TokenResponse(
            id=token.id,
            name=token.name,
            display_name=token.display_name,
            ticker=token.ticker,
            address=token.address,
            categories=token.categories,
            description=token.description,
            decimals=token.decimals,
            trust_score=token.trust_score,
            type="TOKEN",
            logo_uri=token.logo_uri,
        )

    def to_domain(self) -> Token:
        """Convert the TokenResponse to a domain Token."""
        return Token(
            id=self.id,
            name=self.name,
            display_name=self.display_name,
            ticker=self.ticker,
            address=self.address,
            description=self.description,
            decimals=self.decimals,
            categories=self.categories,
            trust_score=self.trust_score,
            logo_uri=self.logo_uri,
        )


class BasketResponse(BaseModel):
    id: str
    name: str
    display_name: str
    ticker: str
    description: str
    decimals: int
    address: str
    categories: list[str]
    trust_score: int
    type: Literal["BASKET"]
    logo_uri: str | None = None

    @staticmethod
    def from_domain(basket: Basket) -> "BasketResponse":
        """Convert the domain Basket to a BasketResponse."""
        return BasketResponse(
            id=basket.id,
            name=basket.name,
            display_name=basket.display_name,
            ticker=basket.ticker,
            address=basket.address,
            description=basket.description,
            decimals=basket.decimals,
            categories=basket.categories,
            trust_score=basket.trust_score,
            logo_uri=basket.logo_uri,
            type="BASKET",
        )

    def to_domain(self) -> Basket:
        """Convert the BasketResponse to a domain Basket."""
        return Basket(
            id=self.id,
            name=self.name,
            display_name=self.display_name,
            ticker=self.ticker,
            description=self.description,
            decimals=self.decimals,
            categories=self.categories,
            trust_score=self.trust_score,
            logo_uri=self.logo_uri,
            address=self.address,
        )


AssetResponse = TokenResponse | BasketResponse


class SimilarAssetsQuery(BaseModel):
    query: str
    type: Literal["TOKEN", "BASKET"] | None


class SimilarAssetsValidResponse(BaseModel):
    assets: list[AssetResponse]
    query: str


class SimilarAssetsResponse(BaseModel):
    data: SimilarAssetsValidResponse | str


class GetAllBasketsResponse(BaseModel):
    baskets: list[BasketResponse]


class GetAssetByIdQuery(BaseModel):
    asset_id: str


class GetAssetByIdValidResponse(BaseModel):
    asset: AssetResponse


class GetAssetByIdResponse(BaseModel):
    data: GetAssetByIdValidResponse | str
