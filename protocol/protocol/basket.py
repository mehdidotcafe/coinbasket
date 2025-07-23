from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from protocol.token import Token


@dataclass
class Basket:
    id: str
    name: str
    description: str
    denomination: Decimal
    tokens: list[Token]

    def __str__(self) -> str:
        return f"""
name: {self.name}
description: {self.description}
type: basket
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
            "description": self.description,
            "denomination": str(self.denomination),
            "tokens": [token.to_dict() for token in self.tokens],
        }
