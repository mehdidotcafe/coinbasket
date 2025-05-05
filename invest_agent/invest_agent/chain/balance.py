from dataclasses import dataclass
from decimal import Decimal

from invest_agent.basket import Token


@dataclass
class Balance:
    token: Token
    amount: Decimal
