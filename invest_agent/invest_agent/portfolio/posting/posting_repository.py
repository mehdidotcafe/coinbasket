from abc import ABC, abstractmethod

from invest_agent.chain.balance import BalanceAtomic
from invest_agent.portfolio.posting.posting import Posting
from protocol.asset import Asset


class PostingRepository(ABC):
    @abstractmethod
    async def create_posting(self, posting: Posting) -> Posting:
        """Save an posting to the repository."""
        raise NotImplementedError

    @abstractmethod
    async def get_holding_balances(self) -> list[BalanceAtomic]:
        """Get the holding balances from the repository for each held asset."""
        raise NotImplementedError

    async def get_holding_balance(self, asset: Asset) -> BalanceAtomic:
        """Get the holding balance for a specific asset."""
        raise NotImplementedError
