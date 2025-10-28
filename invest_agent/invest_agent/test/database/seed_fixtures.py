from pytest_asyncio import fixture
from invest_agent.investment.order.infrastructure.sql_alchemy_order_repository import (
    OrderModel,
)
from invest_agent.investment.order.order import Order
from invest_agent.investment.transaction.infrastructure.sql_alchemy_transaction_repository import (
    TransactionModel,
)
from invest_agent.investment.transaction.transaction import Transaction
from invest_agent.portfolio.posting.infrastructure.sql_alchemy_posting_repository import (
    PostingModel,
)
from invest_agent.portfolio.posting.posting import Posting
from invest_agent.test.database.make_session import make_session


@fixture(scope="function")
async def seed_fixtures(
    orders: list[Order], transactions: list[Transaction], postings: list[Posting]
):
    print("Seeding fixtures...")
    print(orders)
    print(transactions)
    print(postings)
    async with make_session() as session:
        async with session.begin():
            for order in orders:
                session.add(OrderModel.from_domain(order))
            for transaction in transactions:
                session.add(TransactionModel.from_domain(transaction))
            for posting in postings:
                session.add(PostingModel.from_domain(posting))

    yield postings
