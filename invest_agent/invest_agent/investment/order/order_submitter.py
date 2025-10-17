
from abc import ABC, abstractmethod

from invest_agent.investment.order.order import Order


class OrderSubmitter(ABC):
  @abstractmethod
  async def submit_orders(self, orders: list[Order]) -> list[Order]:
    raise NotImplementedError
