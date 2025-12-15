from dataclasses import dataclass
from typing import Literal

from api.chain.balance import BalanceAtomic
from api.investment.fees import Fees
from api.chain.chain import Gas

Id = str

ChainTransactionType = Literal["SIGN", "SEND"]
ChainTransactionStatus = Literal["PENDING", "SUCCESS", "FAIL"]


@dataclass
class ChainTransaction:
    id: Id
    try_id: Id
    order_id: Id
    type: ChainTransactionType
    amount: int
    data: str
    status: ChainTransactionStatus
    hash: str | None = None
    to_address: str | None = None
    gas: Gas | None = None


@dataclass
class Try:
    id: Id
    order_id: Id
    created_at: int
    chain_transactions: list[ChainTransaction]
    provider: str
    buy_balance: BalanceAtomic
    # TODO: Make fees required
    fees: Fees | None = None


OrderType = Literal["SELL", "BUY", "SWAP"]
OrderStatus = Literal["PENDING", "SUCCESS", "FAIL"]
OrderTrigger = Literal["MANUAL", "AUTOMATIC"]
OrderAssetType = Literal["BASKET", "TOKEN"]


@dataclass
class Order:
    id: Id
    sell_balance: BalanceAtomic
    buy_balance: BalanceAtomic
    type: OrderType
    asset_type: OrderAssetType
    tries: list[Try]
    created_at: int
    status: OrderStatus
    trigger: OrderTrigger
    buy_basket_id: Id | None = None
    sell_basket_id: Id | None = None
    parent_order_id: Id | None = None
