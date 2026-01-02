from api.investment.order.infrastructure.sql_alchemy_confirmed_order_repository import (
    ConfirmedOrderModel,
)
from api.investment.order.infrastructure.sql_alchemy_planned_order_repository import (
    PlannedOrderModel,
)
from api.investment.order.infrastructure.sql_alchemy_signable_order_repository import (
    SignableOrderModel,
)
from api.investment.planned_order import PlannedOrder
from api.investment.signable_order import SignableOrder
from api.investment.confirmed_order import ConfirmedOrder

from pytest_asyncio import fixture
from api.test.database.make_session import make_session


@fixture(scope="function")
async def seed_fixtures(
    planned_orders: list[PlannedOrder],
    confirmed_orders: list[ConfirmedOrder],
    signable_orders: list[SignableOrder],
):
    async with make_session() as session:
        async with session.begin():
            for planned_order in planned_orders:
                session.add(PlannedOrderModel.from_domain(planned_order))
            for confirmed_order in confirmed_orders:
                session.add(ConfirmedOrderModel.from_domain(confirmed_order))
            for signable_order in signable_orders:
                session.add(SignableOrderModel.from_domain(signable_order))

    yield planned_orders
