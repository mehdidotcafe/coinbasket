from dataclasses import dataclass
from typing import Literal
from invest_agent.chain.balance import Balance
from invest_agent.investment.fees import Fees

Id = str


@dataclass
class Transaction:
    id: Id
    sell_balance: Balance
    buy_balance: Balance
    type: Literal["SELL", "BUY", "SWAP"]
    created_at: int
    fee: Fees
    transaction_hash: str
    order_id: Id
    trigger: Literal["MANUAL", "AUTOMATIC"]
    basket_id: Id | None = None
