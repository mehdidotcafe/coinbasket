from dataclasses import dataclass

from protocol.token import Token


@dataclass
class Basket:
    id: str
    name: str
    description: str
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
