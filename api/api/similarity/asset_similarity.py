from api.protocol.token import Token
from api.protocol.basket import Basket
from api.protocol.asset_category import AssetCategory


class TokenSimilarity(Token):
    market_cap_usd: int

    def __init__(self, market_cap_usd: int, **kwargs):
        super().__init__(**kwargs)
        self.market_cap_usd = market_cap_usd

    def to_dict(self) -> dict[str, str | int | list[AssetCategory] | None]:
        return super().to_dict() | {"market_cap_usd": self.market_cap_usd}


class BasketSimilarity(Basket):
    market_cap_usd: int

    def __init__(self, market_cap_usd: int, **kwargs):
        super().__init__(**kwargs)
        self.market_cap_usd = market_cap_usd

    def to_dict(self) -> dict[str, str | int | list[AssetCategory] | None]:
        return super().to_dict() | {"market_cap_usd": self.market_cap_usd}


AssetSimilarity = TokenSimilarity | BasketSimilarity
