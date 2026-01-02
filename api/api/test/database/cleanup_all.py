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
from api.portfolio.posting.infrastructure.sql_alchemy_posting_repository import (
    PostingModel,
)
from pytest import fixture
from sqlalchemy import delete
from api.test.database.make_session import make_session

from api.investment.order.infrastructure.sql_alchemy_order_repository import (
    OrderModel,
    OrderTryChainTransactionModel,
    OrderTryModel,
)
from api.investment.transaction.infrastructure.sql_alchemy_transaction_repository import (
    TransactionModel,
)


@fixture(scope="function")
async def cleanup_all():
    yield
    async with make_session() as session:
        async with session.begin():
            await session.execute(delete(PostingModel))
            await session.execute(delete(TransactionModel))
            await session.execute(delete(OrderTryChainTransactionModel))
            await session.execute(delete(OrderTryModel))
            await session.execute(delete(OrderModel))
            await session.execute(delete(ExecutedOrderModel))
            await session.execute(delete(SignableOrderModel))
            await session.execute(delete(ConfirmedOrderModel))
            await session.execute(delete(PlannedOrderModel))
            await session.execute(delete(IntendedOrderModel))
