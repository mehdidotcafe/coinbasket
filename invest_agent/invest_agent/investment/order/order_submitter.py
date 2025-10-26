from abc import ABC, abstractmethod

from invest_agent.investment.order.order import Order


class OrderSubmitter(ABC):
    @abstractmethod
    async def submit_orders(
        self, orders_matrix: list[list[Order]]
    ) -> list[list[Order]]:
        raise NotImplementedError
