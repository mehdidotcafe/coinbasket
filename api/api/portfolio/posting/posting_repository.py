from abc import ABC, abstractmethod
from api.portfolio.holding.holding import Holding
from api.portfolio.posting.posting import Posting
from api.protocol.asset import Asset
from api.database.session import NullableSession


class PostingRepository(ABC):
    @abstractmethod
    async def create_posting(
        self, posting: Posting, session: NullableSession = None
    ) -> Posting:
        """Save a posting to the repository."""
        raise NotImplementedError

    @abstractmethod
    async def get_holding_balances(
        self, session: NullableSession = None
    ) -> list[Holding]:
        """Get the holding balances from the repository for each held asset."""
        raise NotImplementedError

    @abstractmethod
    async def get_holding_balance(
        self, asset: Asset, asset_decimals: int, session: NullableSession = None
    ) -> Holding:
        """Get the holding balance for a specific asset."""
        raise NotImplementedError
