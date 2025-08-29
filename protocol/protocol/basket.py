from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from protocol.token import Token


@dataclass
class Basket:
    id: str
    name: str
    display_name: str
    ticker: str
    description: str
    denomination: Decimal
    # TODO: Use weight
    tokens: list[Token]

    def __str__(self) -> str:
        return f"""
name: {self.name}
display_name: {self.display_name}
ticker: {self.ticker}
description: {self.description}
type: basket
denomination: {str(self.denomination)}
{"\n".join([self.__flatten_token(token, index) for index, token in enumerate(self.tokens)])}
"""

    def __flatten_token(self, token: Token, index: int) -> str:
        return f"""{index + 1}. name: {token.name}
 display_name: {token.display_name}
 ticker: {token.ticker}
 address: {token.address}
"""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "ticker": self.ticker,
            "description": self.description,
            "denomination": str(self.denomination),
            "tokens": [token.to_dict() for token in self.tokens],
        }

    # Baskets use USDT as their pricing token
    def get_pricing_token(self):
        return Token(
            id="bsc:0x55d398326f99059ff775485246999027b3197955",
            name="Tether USD",
            display_name="Tether USD",
            ticker="USDT",
            address="0x55d398326f99059ff775485246999027b3197955",
        )

    def get_denomination(self):
        return self.denomination
