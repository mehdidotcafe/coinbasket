from dataclasses import dataclass
from decimal import Decimal
from invest_agent.chain.chain import ParsedReceipt
from invest_agent.investment.order.order_repository import OrderRepository
from invest_agent.investment.order.order import Order
from invest_agent.investment.order.task.order_on_order_success_task import OnOrderSuccessTask

@dataclass
class OrderRequest:
    id: str

class RevertSucceededOrderTask:
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    async def execute(self, order: Order):
        print("Revert succeeded orders")

class RevertOrderLeftoverTask:
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    async def execute(self, orders: list[Order]):
        print("Revert order leftover")

class EventuallySetParentOrderToFailTask:
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    async def execute(self, order: Order):
        print("Eventually set parent order to fail")

class EventuallySetParentOrderToSuccessTask:
    def __init__(self, order_repository: OrderRepository, on_order_success_task: OnOrderSuccessTask):
        self.order_repository = order_repository
        self.on_order_success = on_order_success_task

    async def execute(self, order: Order):
        print("Eventually set parent order to success")

        parent_order = await self.order_repository.get_order(order.parent_order_id) if order.parent_order_id else None

        if parent_order:
            await self.on_order_success.execute(order=parent_order, order_try=None, parsed_receipt=ParsedReceipt(
                # TODO: Compute real executed balances for parent order
                # Sell leftovers?
                executed_sell_balance=parent_order.sell_balance,
                executed_buy_balance=parent_order.buy_balance,
                rate=Decimal(parent_order.buy_balance.amount_atomic)
                / Decimal(parent_order.sell_balance.amount_atomic),
            ))
