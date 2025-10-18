from dataclasses import dataclass
from typing import TypedDict
from invest_agent.investment.order.order import Order
from invest_agent.investment.order.order_repository import OrderRepository
from invest_agent.investment.order.order_submitter import OrderSubmitter
from shared.id_generator.id_generator import IdGenerator
from temporalio.client import Client


@dataclass
class OrderRequest:
    id: str

    @staticmethod
    def from_domain(order: Order) -> "OrderRequest":
        return OrderRequest(id=order.id)


class Configuration(TypedDict):
    agent_name: str
    temporal_port: int
    temporal_host: str


class TemporalOrderSubmitter(OrderSubmitter):
    def __init__(
        self,
        order_repository: OrderRepository,
        id_generator: IdGenerator,
        configuration: Configuration,
    ):
        self.order_repository = order_repository
        self.id_generator = id_generator
        self.configuration = configuration
        self.client: Client | None = None

        self.task_queue = f"order-submitter-workflow-{self.configuration['agent_name']}"

    async def submit_orders(self, orders: list[Order]) -> list[Order]:
        await self.order_repository.create_orders(orders)

        client = await self.get_client()

        result = await client.start_workflow(
            "TemporalOrderSubmitterWorkflow",
            [OrderRequest.from_domain(order) for order in orders],
            id=f"order-submitter-workflow-{self.id_generator.generate_random_id()}",
            task_queue=self.task_queue,
        )

        print(f"Temporal workflow ID: {result.id}")

        return orders

    async def get_client(self):
        if self.client is None:
            self.client = await Client.connect(
                f"{self.configuration['temporal_host']}:{self.configuration['temporal_port']}"
            )
        return self.client
