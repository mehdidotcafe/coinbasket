from abc import ABC, abstractmethod
from api.investment.executed_order import ExecutedOrder
from api.database.session import NullableSession


class ExecutedOrderRepository(ABC):
    @abstractmethod
    async def save(
        self, executed_order: ExecutedOrder, session: NullableSession = None
    ) -> ExecutedOrder:
        """Save an executed order to the repository."""
        raise NotImplementedError

    @abstractmethod
    async def get(
        self, limit: int | None = None, offset: int | None = None
    ) -> list[ExecutedOrder]:
        """Retrieve executed orders with pagination."""
        raise NotImplementedError
