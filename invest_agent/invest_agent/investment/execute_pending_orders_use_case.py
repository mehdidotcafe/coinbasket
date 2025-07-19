from invest_agent.investment.order.order_repository import OrderRepository
from invest_agent.investment.order.order_submitter import OrderSubmitter


class ExecutePendingOrdersUseCase:
    """Use case for executing pending orders."""

    def __init__(
        self,
        order_repository: OrderRepository,
        order_submitter: OrderSubmitter,
    ):
        self.order_submitter = order_submitter
        self.order_repository = order_repository

    async def execute(self):
        """Execute the pending orders."""
        orders = await self.order_repository.get_pending_orders()

        print(f"Orders: {orders}")

        return await self.order_submitter.submit_orders(orders)
