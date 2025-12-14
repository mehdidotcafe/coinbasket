from dataclasses import dataclass
from typing import Literal

from api.chain.balance import BalanceAtomic

Id = str

PostingType = Literal["SELL", "BUY", "SWAP"]
PostingAssetType = Literal["BASKET", "TOKEN"]


@dataclass
class Posting:
    id: Id
    transaction_id: Id
    asset_balance: BalanceAtomic
    created_at: int
    type: PostingType
    asset_type: PostingAssetType
    basket_id: Id | None = None
    parent_posting_id: Id | None = None
