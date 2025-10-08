from dataclasses import dataclass
from typing import Literal

from invest_agent.chain.balance import BalanceAtomic

Id = str

PostingType = Literal["SELL", "BUY", "SWAP"]


@dataclass
class Posting:
    id: Id
    transaction_id: Id
    asset_balance: BalanceAtomic
    created_at: int
    type: PostingType
    basket_id: Id | None = None
    parent_posting_id: Id | None = None
