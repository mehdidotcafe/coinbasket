from decimal import Decimal
from typing import Literal
from protocol.basket import Basket
from protocol.token import Token
from uagents import Model


class TokenResponse(Model):
    id: str
    name: str
    display_name: str
    ticker: str
    address: str

    @staticmethod
    def from_domain(token: Token) -> "TokenResponse":
        """Convert the domain Token to a TokenResponse."""
        return TokenResponse(
            id=token.id,
            name=token.name,
            display_name=token.display_name,
            ticker=token.ticker,
            address=token.address,
        )

    def to_domain(self) -> Token:
        """Convert the TokenResponse to a domain Token."""
        return Token(
            id=self.id,
            name=self.name,
            display_name=self.display_name,
            ticker=self.ticker,
            address=self.address,
        )


class BasketResponse(Model):
    id: str
    name: str
    display_name: str
    ticker: str
    description: str
    denomination: str
    tokens: list[TokenResponse]

    @staticmethod
    def from_domain(basket: Basket) -> "BasketResponse":
        """Convert the domain Basket to a BasketResponse."""
        return BasketResponse(
            id=basket.id,
            name=basket.name,
            display_name=basket.display_name,
            ticker=basket.ticker,
            description=basket.description,
            denomination=str(basket.denomination),
            tokens=[TokenResponse.from_domain(token) for token in basket.tokens],
        )

    def to_domain(self) -> Basket:
        """Convert the BasketResponse to a domain Basket."""
        return Basket(
            id=self.id,
            name=self.name,
            display_name=self.display_name,
            ticker=self.ticker,
            description=self.description,
            denomination=Decimal(self.denomination),
            tokens=[token.to_domain() for token in self.tokens],
        )


AssetResponse = TokenResponse | BasketResponse


class SimilarAssetsQuery(Model):
    query: str
    agent_key: str
    type: Literal["TOKEN", "BASKET"] | None


class SimilarAssetsValidResponse(Model):
    assets: list[AssetResponse]
    query: str


class SimilarAssetsResponse(Model):
    data: SimilarAssetsValidResponse | str


class GetAllBasketsQuery(Model):
    agent_key: str


class GetAllBasketsResponse(Model):
    baskets: list[BasketResponse]


class GetAssetByIdQuery(Model):
    agent_key: str
    asset_id: str


class GetAssetByIdValidResponse(Model):
    asset: AssetResponse


class GetAssetByIdResponse(Model):
    data: GetAssetByIdValidResponse | str
