from dataclasses import dataclass
from typing import Literal
from api.chain.balance import BalanceAtomic
from api.investment.fees import Fees

Id = str

TransactionType = Literal["SELL", "BUY", "SWAP"]
TransactionTrigger = Literal["MANUAL", "AUTOMATIC"]
TransactionAssetType = Literal["BASKET", "TOKEN"]


@dataclass
class Transaction:
    id: Id
    sell_balance: BalanceAtomic
    buy_balance: BalanceAtomic
    executed_sell_balance: BalanceAtomic
    executed_buy_balance: BalanceAtomic
    type: TransactionType
    asset_type: TransactionAssetType
    created_at: int
    order_id: Id
    trigger: TransactionTrigger
    # TODO: Make fees required
    fees: Fees | None = None
    # No transaction hash for parent transactions
    transaction_hash: str | None = None
    buy_basket_id: Id | None = None
    sell_basket_id: Id | None = None
    parent_transaction_id: Id | None = None
