from api.protocol.token import Token
from api.protocol.basket import Basket
from api.protocol.asset_category import AssetCategory


class TokenSimilarity(Token):
    is_canonical: bool
    market_cap_usd: int

    def __init__(self, is_canonical: bool, market_cap_usd: int, **kwargs):
        super().__init__(**kwargs)
        self.is_canonical = is_canonical
        self.market_cap_usd = market_cap_usd

    def to_dict(self) -> dict[str, str | int | list[AssetCategory] | None]:
        return super().to_dict() | {
            "is_canonical": self.is_canonical,
            "market_cap_usd": self.market_cap_usd,
        }


class BasketSimilarity(Basket):
    is_canonical: bool
    market_cap_usd: int

    def __init__(self, is_canonical: bool, market_cap_usd: int, **kwargs):
        super().__init__(**kwargs)
        self.is_canonical = is_canonical
        self.market_cap_usd = market_cap_usd

    def to_dict(self) -> dict[str, str | int | list[AssetCategory] | None]:
        return super().to_dict() | {
            "is_canonical": self.is_canonical,
            "market_cap_usd": self.market_cap_usd,
        }


AssetSimilarity = TokenSimilarity | BasketSimilarity
