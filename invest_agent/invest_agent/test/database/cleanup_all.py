from pytest import fixture
from invest_agent.test.database.make_session import make_session

from invest_agent.investment.order.infrastructure.sql_alchemy_order_repository import (
    OrderModel,
    OrderTryChainTransactionModel,
    OrderTryModel,
)
from invest_agent.investment.transaction.infrastructure.sql_alchemy_transaction_repository import (
    TransactionModel,
)


@fixture(scope="function")
async def cleanup_all():
    yield
    async with make_session() as session:
        async with session.begin():
            await session.execute(OrderModel.__table__.delete())
            await session.execute(OrderTryModel.__table__.delete())
            await session.execute(OrderTryChainTransactionModel.__table__.delete())
            await session.execute(TransactionModel.__table__.delete())
