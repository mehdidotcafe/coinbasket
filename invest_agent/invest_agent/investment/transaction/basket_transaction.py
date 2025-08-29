from dataclasses import dataclass
from typing import Literal
from invest_agent.chain.balance import Balance
from invest_agent.investment.order.basket_order import BasketOrder


Id = str

TransactionType = Literal["SELL", "BUY", "SWAP"]
TransactionTrigger = Literal["MANUAL", "AUTOMATIC"]


@dataclass
class BasketTransaction:
    id: Id
    sell_balance: Balance
    buy_balance: Balance
    type: TransactionType
    created_at: int
    trigger: TransactionTrigger
    basket_order: BasketOrder | None = None
    basket_id: Id | None = None
