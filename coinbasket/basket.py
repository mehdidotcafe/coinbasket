from dataclasses import dataclass
from typing_extensions import List


@dataclass
class Coin:
    name: str
    display_name: str
    ticker: str
    address: str


@dataclass
class Basket:
    name: str
    coins: List[Coin]
