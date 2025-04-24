from dataclasses import dataclass
from typing_extensions import List


@dataclass
class Token:
    name: str
    display_name: str
    ticker: str
    address: str


@dataclass
class Basket:
    name: str
    tokens: List[Token]
