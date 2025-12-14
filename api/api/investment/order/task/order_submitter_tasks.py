from dataclasses import dataclass
from decimal import Decimal
from api.chain.chain import ParsedReceipt
from api.investment.order.order_repository import OrderRepository
from api.investment.order.order import Order
from api.investment.order.task.order_on_order_success_task import (
    OnOrderSuccessTask,
)
from api.investment.transaction.transaction import Transaction


@dataclass
class OrderRequest:
    id: str


class RevertSucceededOrderTask:
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    async def execute(self, order: Order):
        print("RevertSucceededOrderTask")


class RevertOrderLeftoverTask:
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    async def execute(self, orders: list[Order]):
        # TODO: Sell leftover tokens back to native token
        print("RevertOrderLeftoverTask")


class EventuallySetParentOrderToFailTask:
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    async def execute(self, order: Order):
        print("EventuallySetParentOrderToFailTask")


class EventuallySetParentOrderToSuccessTask:
    def __init__(
        self,
        order_repository: OrderRepository,
        on_order_success_task: OnOrderSuccessTask,
    ):
        self.order_repository = order_repository
        self.on_order_success = on_order_success_task

    async def execute(
        self, transactions: list[Transaction], parent_order: Order | None
    ):
        if parent_order:
            min_fill = self._get_min_child_transaction_fill(transactions)

            executed_buy_balance = parent_order.buy_balance * (
                min_fill / Decimal("100")
            )

            return await self.on_order_success.execute(
                order=parent_order,
                order_try=None,
                parsed_receipt=ParsedReceipt(
                    executed_sell_balance=parent_order.sell_balance,
                    executed_buy_balance=executed_buy_balance,
                    rate=Decimal(
                        (parent_order.buy_balance / executed_buy_balance).amount_atomic
                    ),
                ),
            )
        return None

    def _get_min_child_transaction_fill(
        self, transactions: list[Transaction]
    ) -> Decimal:
        return min(
            [
                Decimal(transaction.executed_buy_balance.amount_atomic)
                * 100
                / Decimal(transaction.buy_balance.amount_atomic)
                for transaction in transactions
            ]
        )
