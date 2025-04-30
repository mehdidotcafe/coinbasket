from dataclasses import dataclass

from coinbasket.basket import Token
from coinbasket.chain.balance import Balance


@dataclass
class InvestmentResultBid:
    token: Token
    balance_in: Balance
    balance_out: Balance


@dataclass
class InvestmentResult:
    bids: list[InvestmentResultBid]
