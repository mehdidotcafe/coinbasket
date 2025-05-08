from dataclasses import dataclass
from decimal import Decimal

from protocol.token import Token


@dataclass
class Balance:
    token: Token
    amount: Decimal
