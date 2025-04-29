from dataclasses import dataclass

from coinbasket.basket import Token


@dataclass
class Balance:
    token: Token
    amount: float
