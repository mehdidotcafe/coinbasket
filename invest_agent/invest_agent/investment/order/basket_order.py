from dataclasses import dataclass
from typing import Literal

from invest_agent.chain.balance import Balance

Id = str

OrderType = Literal["SELL", "BUY", "SWAP"]
OrderTrigger = Literal["MANUAL", "AUTOMATIC"]


@dataclass
class BasketOrder:
    id: Id
    sell_balance: Balance
    buy_balance: Balance
    type: OrderType
    created_at: int
    trigger: OrderTrigger
    basket_id: Id | None = None
