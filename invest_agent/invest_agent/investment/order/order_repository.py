from abc import ABC, abstractmethod

from invest_agent.investment.order.order import Id, Order, Try


class OrderRepository(ABC):
    @abstractmethod
    async def create_order(self, order: Order) -> Order:
        """Save an order to the repository."""
        raise NotImplementedError

    @abstractmethod
    async def add_order_try(self, order_id: Id, order_try: Try) -> Try:
        """Add a try to an existing order."""
        raise NotImplementedError

    @abstractmethod
    async def set_order_to_success(self, order_id: Id) -> None:
        """Set an order status to success."""
        raise NotImplementedError

    @abstractmethod
    async def set_order_to_failed(self, order_id: Id) -> None:
        """Set an order status to failed."""
        raise NotImplementedError

    @abstractmethod
    async def get_pending_orders(self) -> list[Order]:
        """Fetch all pending orders."""
        raise NotImplementedError

    @abstractmethod
    async def set_order_try_chain_transaction_to_success(
        self, chain_transaction_id: Id
    ) -> None:
        """Set a chain transaction status to success."""
        raise NotImplementedError

    @abstractmethod
    async def set_order_try_chain_transaction_to_fail(
        self, chain_transaction_id: Id
    ) -> None:
        """Set a chain transaction status to fail."""
        raise NotImplementedError
