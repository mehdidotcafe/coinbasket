from dataclasses import dataclass
from typing import Literal

from invest_agent.chain.balance import Balance
from protocol.token import Token


@dataclass
class Bid:
    token: Token
    sell_balance: Balance
    buy_balance: Balance


@dataclass
class BasketInvestment:
    name: str
    description: str
    type: str
    invested_at: str
    bids: list[Bid]
    status: Literal["invested"]
