from abc import ABC, abstractmethod
from api.investment.confirmed_order import ConfirmedOrder
from api.database.session import NullableSession


class ConfirmedOrderRepository(ABC):
    @abstractmethod
    async def save(
        self, confirmed_order: ConfirmedOrder, session: NullableSession = None
    ) -> ConfirmedOrder:
        """Save a confirmed order to the repository."""
        raise NotImplementedError
