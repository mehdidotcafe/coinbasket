from dataclasses import dataclass
from typing import Literal

from invest_agent.chain.balance import Balance
from invest_agent.investment.fees import Fees
from invest_agent.investment.order.basket_order import BasketOrder

Id = str

ChainTransactionType = Literal["SIGN", "SEND"]
ChainTransactionStatus = Literal["PENDING", "SUCCESS", "FAIL"]


@dataclass
class ChainTransaction:
    id: Id
    try_id: Id
    order_id: Id
    type: ChainTransactionType
    data: str
    hash: str
    status: ChainTransactionStatus


@dataclass
class Try:
    id: Id
    order_id: Id
    created_at: int
    chain_transactions: list[ChainTransaction]
    provider: str
    buy_balance: Balance
    # TODO: Make fees required
    fees: Fees | None = None


OrderType = Literal["SELL", "BUY", "SWAP"]
OrderStatus = Literal["PENDING", "SUCCESS", "FAIL"]
OrderTrigger = Literal["MANUAL", "AUTOMATIC"]


@dataclass
class Order:
    id: Id
    sell_balance: Balance
    buy_balance: Balance
    type: OrderType
    tries: list[Try]
    created_at: int
    status: OrderStatus
    trigger: OrderTrigger
    basket_id: Id | None = None
    basket_order: BasketOrder | None = None
