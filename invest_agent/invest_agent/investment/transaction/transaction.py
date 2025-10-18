from dataclasses import dataclass
from typing import Literal
from invest_agent.chain.balance import BalanceAtomic
from invest_agent.investment.fees import Fees

Id = str

TransactionType = Literal["SELL", "BUY", "SWAP"]
TransactionTrigger = Literal["MANUAL", "AUTOMATIC"]


@dataclass
class Transaction:
    id: Id
    sell_balance: BalanceAtomic
    buy_balance: BalanceAtomic
    executed_sell_balance: BalanceAtomic
    executed_buy_balance: BalanceAtomic
    type: Literal["SELL", "BUY", "SWAP"]
    created_at: int
    order_id: Id
    trigger: Literal["MANUAL", "AUTOMATIC"]
    # TODO: Make fees required
    fees: Fees | None = None
    # No transaction hash for parent transactions
    transaction_hash: str | None = None
    basket_id: Id | None = None
    parent_transaction_id: Id | None = None
