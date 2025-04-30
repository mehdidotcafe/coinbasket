from dataclasses import dataclass
from decimal import Decimal

from coinbasket.basket import Token


@dataclass
class Balance:
    token: Token
    amount: Decimal
