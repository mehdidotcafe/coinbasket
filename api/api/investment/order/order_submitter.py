from abc import ABC, abstractmethod

from api.investment.order.order import Order


class OrderSubmitter(ABC):
    @abstractmethod
    async def submit_orders(
        self, orders_matrix: list[list[Order]]
    ) -> list[list[Order]]:
        raise NotImplementedError
