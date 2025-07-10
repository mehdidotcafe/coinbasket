from dataclasses import dataclass
from typing import Literal

from invest_agent.chain.balance import Balance
from invest_agent.investment.fees import Fees
from protocol.token import Token

Id = str


@dataclass
class Try:
    id: Id
    created_at: int
    fees: Fees
    transaction_hash: str
    provider: Literal["0X_PROTOCOL"]
    buy_balance: Balance


@dataclass
class Order:
    id: Id
    sell_balance: Balance
    buy_token: Token
    type: Literal["SELL", "BUY", "SWAP"]
    tries: list[Try]
    created_at: int
    status: Literal["PENDING", "SUCCESS", "FAIL"]
    trigger: Literal["MANUAL", "AUTOMATIC"]
    basket_id: Id | None = None
