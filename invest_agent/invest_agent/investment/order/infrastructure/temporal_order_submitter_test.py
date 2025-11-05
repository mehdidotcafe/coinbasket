from invest_agent.chain.balance import BalanceAtomic
from pytest import fixture, mark
from unittest import mock
from invest_agent.investment.order.infrastructure.temporal_order_submitter import (
    TemporalOrderSubmitter,
    Configuration,
    OrderRequest,
)
from invest_agent.investment.order.order import Order
from invest_agent.investment.order.order_repository import OrderRepository
from shared.id_generator.id_generator import IdGenerator
from temporalio.client import Client


@fixture
def order_repository():
    return mock.Mock(spec=OrderRepository)


@fixture
def id_generator():
    gen = mock.Mock(spec=IdGenerator)
    gen.generate_random_id.side_effect = ["test-id-1", "test-id-2"]
    return gen


@fixture
def configuration():
    return Configuration(
        agent_name="test-agent", temporal_port=7233, temporal_host="localhost"
    )


@fixture
def temporal_client():
    client = mock.AsyncMock(spec=Client)
    client.start_workflow = mock.AsyncMock()
    client.connect = mock.AsyncMock(return_value=client)
    return client


@mark.asyncio
async def test_temporal_order_submitter_submit_orders(
    order_repository: OrderRepository,
    id_generator: IdGenerator,
    configuration: Configuration,
    temporal_client: type[Client],
):
    order1 = Order(
        id="order1",
        sell_balance=mock.Mock(spec=BalanceAtomic),
        buy_balance=mock.Mock(spec=BalanceAtomic),
        type="BUY",
        asset_type="TOKEN",
        tries=[],
        created_at=0,
        status="PENDING",
        trigger="MANUAL",
        buy_basket_id="basket1",
    )
    order2 = Order(
        id="order2",
        sell_balance=mock.Mock(spec=BalanceAtomic),
        buy_balance=mock.Mock(spec=BalanceAtomic),
        type="SELL",
        asset_type="TOKEN",
        tries=[],
        created_at=0,
        status="PENDING",
        trigger="MANUAL",
        buy_basket_id="basket2",
    )

    order3 = Order(
        id="order3",
        sell_balance=mock.Mock(spec=BalanceAtomic),
        buy_balance=mock.Mock(spec=BalanceAtomic),
        type="SELL",
        asset_type="TOKEN",
        tries=[],
        created_at=0,
        status="PENDING",
        trigger="MANUAL",
        buy_basket_id="basket2",
    )
    orders_matrix = [[order1], [order2, order3]]

    submitter = TemporalOrderSubmitter(
        order_repository=order_repository,
        id_generator=id_generator,
        configuration=configuration,
        TemporalClient=temporal_client,
    )

    result = await submitter.submit_orders(orders_matrix)

    order_repository.create_orders.assert_called_once_with([order1, order2, order3])

    temporal_client.connect.return_value.assert_has_calls(
        [
            mock.call.start_workflow(
                "TemporalOrderSubmitterWorkflow",
                [
                    OrderRequest(
                        id="order1",
                    ),
                ],
                id="order-submitter-workflow-test-id-1",
                task_queue="order-submitter-workflow-test-agent",
            ),
            mock.call.start_workflow(
                "TemporalOrderSubmitterWorkflow",
                [
                    OrderRequest(
                        id="order2",
                    ),
                    OrderRequest(
                        id="order3",
                    ),
                ],
                id="order-submitter-workflow-test-id-2",
                task_queue="order-submitter-workflow-test-agent",
            ),
        ]
    )

    assert result == orders_matrix
