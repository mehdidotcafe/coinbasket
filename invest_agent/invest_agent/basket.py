from dataclasses import dataclass


@dataclass
class Token:
    name: str
    display_name: str
    ticker: str
    address: str


@dataclass
class Basket:
    name: str
    description: str
    tokens: list[Token]
