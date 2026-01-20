from abc import ABC, abstractmethod
from api.investment.intended_order import IntendedOrder
from api.database.session import NullableSession


class IntendedOrderRepository(ABC):
    @abstractmethod
    async def save(
        self, intended_order: IntendedOrder, session: NullableSession = None
    ) -> IntendedOrder:
        """Save an intended order to the repository."""
        raise NotImplementedError
