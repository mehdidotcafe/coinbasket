from dataclasses import dataclass
from typing import Literal

from invest_agent.chain.balance import BalanceAtomic
from invest_agent.investment.transaction.basket_transaction import BasketTransaction
from protocol.token import Token

Id = str

PostingType = Literal["SELL", "BUY", "SWAP"]


@dataclass
class Posting:
    id: Id
    transaction_id: Id
    # Executed asset balance
    asset_balance: BalanceAtomic[Token]
    created_at: int
    type: PostingType
    basket_id: Id | None = None
    basket_transaction: BasketTransaction | None = None
