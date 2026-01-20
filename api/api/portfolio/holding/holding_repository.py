from abc import ABC, abstractmethod
from api.portfolio.holding.holding import Holding
from api.protocol.asset import Asset
from api.address.address import Address


class HoldingRepository(ABC):
    @abstractmethod
    async def get_holding_balances(
        self,
        address: Address,
        assets: list[Asset],
    ) -> list[Holding]:
        """Get the holding balances from the repository for each held asset."""
        raise NotImplementedError

    @abstractmethod
    async def get_holding_balance(
        self,
        address: Address,
        asset: Asset,
    ) -> Holding:
        """Get the holding balance for a specific asset."""
        raise NotImplementedError
