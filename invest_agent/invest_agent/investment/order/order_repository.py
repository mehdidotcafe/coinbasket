
from abc import ABC, abstractmethod
from invest_agent.investment.order.order import Id, Order, OrderStatus, Try
from invest_agent.database.session import NullableSession


class OrderRepository(ABC):
    @abstractmethod
    async def set_order_try_chain_transaction_hash(
        self, chain_transaction_id: Id, transaction_hash: str, session: NullableSession = None
    ) -> None:
        """Set the hash for a chain transaction in an order try."""
        raise NotImplementedError
    @abstractmethod
    async def create_order(self, order: Order, session: NullableSession = None) -> Order:
        """Save an order to the repository."""
        raise NotImplementedError

    @abstractmethod
    async def create_orders(self, orders: list[Order], session: NullableSession = None) -> list[Order]:
        """Save multiple orders to the repository."""
        raise NotImplementedError

    @abstractmethod
    async def add_order_try(self, order_id: Id, order_try: Try, session: NullableSession = None) -> Try:
        """Add a try to an existing order."""
        raise NotImplementedError

    @abstractmethod
    async def get_order_try(self, order_try_id: Id, session: NullableSession = None) -> Try | None:
        """Fetch an order try by its ID."""
        raise NotImplementedError

    @abstractmethod
    async def set_order_to_success(self, order_id: Id, session: NullableSession = None) -> None:
        """Set an order status to success."""
        raise NotImplementedError

    @abstractmethod
    async def set_order_to_fail(self, order_id: Id, session: NullableSession = None) -> None:
        """Set an order status to failed."""
        raise NotImplementedError

    @abstractmethod
    async def get_pending_orders(self, session: NullableSession = None) -> list[Order]:
        """Fetch all pending orders."""
        raise NotImplementedError

    @abstractmethod
    async def get_orders(
        self, status: OrderStatus | None = None, limit: int | None = None, offset: int | None = None, parent_order_id: Id | None = None, session: NullableSession = None
    ) -> list[Order]:
        """Fetch all orders with the given status if passed. Returns all orders otherwise."""
        raise NotImplementedError

    @abstractmethod
    async def get_order(self, order_id: Id, session: NullableSession = None) -> Order | None:
        """Fetch an order by its ID."""
        raise NotImplementedError

    @abstractmethod
    async def set_order_try_chain_transaction_to_success(
        self, chain_transaction_id: Id, session: NullableSession = None
    ) -> None:
        """Set a chain transaction status to success."""
        raise NotImplementedError

    @abstractmethod
    async def set_order_try_chain_transaction_to_fail(
        self, chain_transaction_id: Id, session: NullableSession = None
    ) -> None:
        """Set a chain transaction status to fail."""
        raise NotImplementedError

    @abstractmethod
    async def set_order_try_chain_transactions_to_fail(
        self, order_try_id: Id, session: NullableSession = None
    ) -> None:
        """Set a order try chain transactions status to fail."""
        raise NotImplementedError
