from api.investment.order.infrastructure.sql_alchemy_confirmed_order_repository import (
    ConfirmedOrderModel,
)
from api.investment.order.infrastructure.sql_alchemy_executed_order_repository import (
    ExecutedOrderModel,
)
from api.investment.order.infrastructure.sql_alchemy_intended_order_repository import (
    IntendedOrderModel,
)
from api.investment.order.infrastructure.sql_alchemy_planned_order_repository import (
    PlannedOrderModel,
)
from api.investment.order.infrastructure.sql_alchemy_signable_order_repository import (
    SignableOrderModel,
)

from pytest import fixture
from sqlalchemy import delete
from api.test.database.make_session import make_session


@fixture(scope="function")
async def cleanup_all():
    yield
    async with make_session() as session:
        async with session.begin():
            await session.execute(delete(ExecutedOrderModel))
            await session.execute(delete(SignableOrderModel))
            await session.execute(delete(ConfirmedOrderModel))
            await session.execute(delete(PlannedOrderModel))
            await session.execute(delete(IntendedOrderModel))
