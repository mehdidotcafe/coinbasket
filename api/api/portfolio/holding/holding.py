from dataclasses import dataclass

from api.chain.balance import BalanceAtomic
from api.protocol.token import Token


@dataclass
class Holding:
    balance: BalanceAtomic
    children: list[BalanceAtomic[Token]] | None
