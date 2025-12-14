import asyncio
from dataclasses import dataclass
from typing import TypedDict
from api.investment.order.order import Order
from api.investment.order.order_repository import OrderRepository
from api.investment.order.order_submitter import OrderSubmitter
from shared.id_generator.id_generator import IdGenerator
from temporalio.client import Client
from itertools import chain


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
        TemporalClient: type[Client],
    ):
        self.order_repository = order_repository
        self.id_generator = id_generator
        self.configuration = configuration
        self.TemporalClient = TemporalClient
        self.client: Client | None = None

        self.task_queue = f"order-submitter-workflow-{self.configuration['agent_name']}"

    async def submit_orders(
        self, orders_matrix: list[list[Order]]
    ) -> list[list[Order]]:
        await self.order_repository.create_orders(
            list(chain.from_iterable(orders_matrix))
        )

        client = await self.get_client()

        tasks = [
            client.start_workflow(
                "TemporalOrderSubmitterWorkflow",
                [
                    OrderRequest.from_domain(order)
                    for order in orders
                    if order.asset_type != "BASKET"
                ],
                id=f"order-submitter-workflow-{self.id_generator.generate_random_id()}",
                task_queue=self.task_queue,
            )
            for orders in orders_matrix
        ]

        await asyncio.gather(*tasks, return_exceptions=True)

        return orders_matrix

    async def get_client(self):
        if self.client is None:
            self.client = await self.TemporalClient.connect(
                f"{self.configuration['temporal_host']}:{self.configuration['temporal_port']}"
            )
        return self.client
