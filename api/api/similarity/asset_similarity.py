from api.protocol.token import Token
from api.protocol.basket import Basket
from api.protocol.asset_category import AssetCategory


class TokenSimilarity(Token):
    is_canonical: int
    market_cap_usd: int
    trust_score: int

    def __init__(
        self, is_canonical: int, market_cap_usd: int, trust_score: int, **kwargs
    ):
        super().__init__(**kwargs)
        self.is_canonical = is_canonical
        self.market_cap_usd = market_cap_usd
        self.trust_score = trust_score

    def to_document(self) -> str:
        return f"""
name: {self.name}
display_name: {self.display_name}
description: {self.description}
ticker: {self.ticker}
address: {self.address}
categories: {", ".join(str(category) for category in self.categories)}
"""

    def to_dict(self) -> dict[str, str | int | list[AssetCategory] | None]:
        return super().to_dict() | {
            "is_canonical": self.is_canonical,
            "market_cap_usd": self.market_cap_usd,
            "trust_score": self.trust_score,
        }


class BasketSimilarity(Basket):
    is_canonical: int
    market_cap_usd: int
    trust_score: int

    def __init__(
        self, is_canonical: int, market_cap_usd: int, trust_score: int, **kwargs
    ):
        super().__init__(**kwargs)
        self.is_canonical = is_canonical
        self.market_cap_usd = market_cap_usd
        self.trust_score = trust_score

    def to_document(self) -> str:
        return f"""
name: {self.name}
display_name: {self.display_name}
description: {self.description}
ticker: {self.ticker}
address: {self.address}
categories: {", ".join(self.categories)}
"""

    def to_dict(self) -> dict[str, str | int | list[AssetCategory] | None]:
        return super().to_dict() | {
            "is_canonical": self.is_canonical,
            "market_cap_usd": self.market_cap_usd,
            "trust_score": self.trust_score,
        }


AssetSimilarity = TokenSimilarity | BasketSimilarity
