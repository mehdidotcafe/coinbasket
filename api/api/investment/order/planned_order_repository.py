from abc import ABC, abstractmethod
from api.investment.planned_order import PlannedOrder
from api.database.session import NullableSession


class PlannedOrderRepository(ABC):
    @abstractmethod
    async def save(
        self, planned_order: PlannedOrder, session: NullableSession = None
    ) -> PlannedOrder:
        """Save an planned order to the repository."""
        raise NotImplementedError
