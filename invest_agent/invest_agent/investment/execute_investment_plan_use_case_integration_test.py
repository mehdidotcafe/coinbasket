from asyncio import sleep
from decimal import Decimal
from typing import Any
from invest_agent.chain.balance import Balance, BalanceAtomic
from invest_agent.investment.order.infrastructure.sql_alchemy_order_repository import (
    OrderModel,
)
from invest_agent.investment.transaction.infrastructure.sql_alchemy_transaction_repository import (
    TransactionModel,
)
from invest_agent.investment.transaction.transaction import Transaction
from invest_agent.portfolio.posting.infrastructure.sql_alchemy_posting_repository import (
    PostingModel,
)
from invest_agent.portfolio.posting.posting import Posting
from invest_agent.investment.order.order import Order
from pytest import fixture, mark

from invest_agent.main import (
    execute_investment_plan_use_case,
)
from invest_agent.investment.investment_planner.investment_plan import (
    InvestmentPlan,
    InvestmentPlanStep,
)

from protocol.fixture.token import btc_token, sol_token, usdt_token

from sqlalchemy import select

from invest_agent.test.database.make_session import make_session

from invest_agent.test.database.cleanup_all import cleanup_all  # noqa: F401


@fixture
def orders():
    return [
        Order(
            id="f9bd9283-fea4-4e2d-9f3c-4ad0b66503ef",
            sell_balance=BalanceAtomic(
                asset=usdt_token,
                amount=Decimal("100.00"),
                amount_atomic=int(10000 * 10**16),
                decimals=18,
            ),
            buy_balance=BalanceAtomic(
                asset=usdt_token,
                amount=Decimal("100.00"),
                amount_atomic=int(10000 * 10**16),
                decimals=18,
            ),
            type="BUY",
            asset_type="TOKEN",
            tries=[],
            created_at=0,
            status="SUCCESS",
            trigger="MANUAL",
        ),
    ]


@fixture
def transactions():
    return [
        Transaction(
            id="f9bd9283-fea4-4e2d-9f3c-4ad0b66503ef",
            sell_balance=BalanceAtomic(
                asset=usdt_token,
                amount=Decimal("100.00"),
                amount_atomic=int(10000 * 10**16),
                decimals=18,
            ),
            buy_balance=BalanceAtomic(
                asset=usdt_token,
                amount=Decimal("100.00"),
                amount_atomic=int(10000 * 10**16),
                decimals=18,
            ),
            executed_sell_balance=BalanceAtomic(
                asset=usdt_token,
                amount=Decimal("102.22"),
                amount_atomic=int(10222 * 10**16),
                decimals=18,
            ),
            executed_buy_balance=BalanceAtomic(
                asset=usdt_token,
                amount=Decimal("103.33"),
                amount_atomic=int(10333 * 10**16),
                decimals=18,
            ),
            type="BUY",
            created_at=0,
            transaction_hash="0x1234567890abcdef",
            order_id="f9bd9283-fea4-4e2d-9f3c-4ad0b66503ef",
            trigger="MANUAL",
        )
    ]



@fixture
def postings():
    return [
        Posting(
            id="6dcba8f1-a95e-4d3f-b9c8-006c12082d0a",
            transaction_id="f9bd9283-fea4-4e2d-9f3c-4ad0b66503ef",
            asset_balance=BalanceAtomic(
                asset=usdt_token,
                amount=Decimal("1000"),
                amount_atomic=int(1000 * 10**18),
                decimals=18,
            ),
            created_at=0,
            type="BUY",
        ),
    ]


@fixture
def investment_plan_only_tokens():
    return InvestmentPlan(
        steps=[
            InvestmentPlanStep(
                buy_balance=Balance(
                    amount=Decimal("1"),
                    asset=sol_token,
                ),
                sell_balance=Balance(
                    asset=usdt_token,
                    amount=Decimal("7"),
                ),
            ),
            InvestmentPlanStep(
                buy_balance=Balance(
                    asset=btc_token,
                    amount=Decimal("0.001"),
                ),
                sell_balance=Balance(
                    asset=usdt_token,
                    amount=Decimal(1),
                ),
            ),
        ]
    )

@fixture(scope="function")
async def seed_fixtures(
    orders: list[Order],
    transactions: list[Transaction],
    postings: list[Posting]
):
    async with make_session() as session:
        async with session.begin():
            for order in orders:
                session.add(OrderModel.from_domain(order))
            for transaction in transactions:
                session.add(TransactionModel.from_domain(transaction))
            for posting in postings:
                session.add(PostingModel.from_domain(posting))

    yield postings



async def fetch_all_orders(excluded_order_ids: list[str] = []):
    async with make_session() as session:
        result = await session.execute(
            select(OrderModel)
            .where(~OrderModel.id.in_(excluded_order_ids))
            .order_by(OrderModel.asset_type.asc())
        )
        rows = result.scalars().all()
        return rows


async def fetch_all_transactions(excluded_transaction_ids: list[str] = []):
    async with make_session() as session:
        result = await session.execute(
            select(TransactionModel)
            .where(~TransactionModel.id.in_(excluded_transaction_ids))
            .order_by(TransactionModel.created_at.asc())
        )
        rows = result.scalars().all()
        return rows


async def fetch_all_postings(excluded_posting_ids: list[str] = []):
    async with make_session() as session:
        result = await session.execute(
            select(PostingModel)
            .where(~PostingModel.id.in_(excluded_posting_ids))
            .order_by(PostingModel.created_at.asc())
        )
        rows = result.scalars().all()
        return rows


async def wait_for_orders():
    await sleep(5)


@mark.asyncio(loop_scope="session")
async def test_integration_execute_investment_plan_use_case_only_tokens(
    investment_plan_only_tokens: InvestmentPlan,
    seed_fixtures: Any,  # noqa: F811
    cleanup_all: Any,  # noqa: F811
):
    await execute_investment_plan_use_case.execute(investment_plan_only_tokens)

    await wait_for_orders()

    orders = list(await fetch_all_orders(["f9bd9283-fea4-4e2d-9f3c-4ad0b66503ef"]))

    assert len(orders) == 2

    # Token orders
    assert orders[0].status == "SUCCESS"
    assert orders[0].asset_type == "TOKEN"

    assert orders[1].status == "SUCCESS"
    assert orders[1].asset_type == "TOKEN"

    transactions = list(await fetch_all_transactions(["f9bd9283-fea4-4e2d-9f3c-4ad0b66503ef"]))

    assert len(transactions) == 2

    # Check if all transactions are linked to the correct orders regardless of order
    assert all(
        transaction.order_id in [order.id for order in orders]
        for transaction in transactions
    )

    postings = list(await fetch_all_postings(["6dcba8f1-a95e-4d3f-b9c8-006c12082d0a"]))

    assert len(postings) == 4

    assert all(
        transaction.order_id in [order.id for order in orders]
        for transaction in transactions
    )

    # Check if all buy balances are reflected in postings
    assert all([
        posting.id in [f"{transaction.id}-{suffix}" for transaction in transactions for suffix in ("IN", "OUT")]
        for posting in postings
    ])