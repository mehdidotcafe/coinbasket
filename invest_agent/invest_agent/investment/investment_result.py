from dataclasses import dataclass

from invest_agent.basket import Token
from invest_agent.chain.balance import Balance


@dataclass
class InvestmentResultBid:
    token: Token
    balance_in: Balance
    balance_out: Balance


@dataclass
class InvestmentResult:
    bids: list[InvestmentResultBid]
