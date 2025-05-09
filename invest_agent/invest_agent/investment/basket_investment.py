from dataclasses import dataclass

from invest_agent.chain.balance import Balance
from protocol.token import Token


@dataclass
class Bid:
    token: Token
    balance_in: Balance
    balance_out: Balance


@dataclass
class BasketInvestment:
    name: str
    description: str
    type: str
    invested_at: str
    bids: list[Bid]
