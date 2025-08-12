from dataclasses import dataclass
from typing import Literal
from invest_agent.chain.balance import BalanceAtomic
from invest_agent.investment.fees import Fees
from invest_agent.investment.transaction.basket_transaction import BasketTransaction
from protocol.token import Token

Id = str


@dataclass
class Transaction:
    id: Id
    sell_balance: BalanceAtomic[Token]
    buy_balance: BalanceAtomic[Token]
    type: Literal["SELL", "BUY", "SWAP"]
    created_at: int
    transaction_hash: str
    order_id: Id
    trigger: Literal["MANUAL", "AUTOMATIC"]
    # TODO: Make fees required
    fees: Fees | None = None
    basket_id: Id | None = None
    basket_transaction: BasketTransaction | None = None
