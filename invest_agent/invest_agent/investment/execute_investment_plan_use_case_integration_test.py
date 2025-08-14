from asyncio import sleep
from decimal import Decimal
from typing import Any
from invest_agent.chain.balance import Balance
from invest_agent.investment.order.infrastructure.sql_alchemy_order_repository import (
    OrderModel,
)
from invest_agent.investment.transaction.infrastructure.sql_alchemy_transaction_repository import (
    TransactionModel,
)
from invest_agent.portfolio.posting.infrastructure.sql_alchemy_posting_repository import (
    PostingModel,
)
from pytest import fixture, mark

from invest_agent.main import (
    execute_investment_plan_use_case,
)
from invest_agent.investment.investment_planner.investment_plan import (
    InvestmentPlan,
    InvestmentPlanStep,
)
from protocol.fixture.basket import (
    memecoinmania_basket,
)
from protocol.fixture.token import btc_token, bnb_token

from sqlalchemy import select

from invest_agent.test.database.make_session import make_session

from invest_agent.test.database.cleanup_all import cleanup_all  # noqa: F401


@fixture
def investment_plan():
    return InvestmentPlan(
        steps=[
            InvestmentPlanStep(
                buy_balance=Balance(
                    amount=Decimal("1"),
                    asset=memecoinmania_basket,
                ),
                sell_balance=Balance(
                    asset=bnb_token,
                    amount=Decimal("7"),
                ),
            ),
            InvestmentPlanStep(
                buy_balance=Balance(
                    asset=btc_token,
                    amount=Decimal("0.001"),
                ),
                sell_balance=Balance(
                    asset=bnb_token,
                    amount=Decimal(1),
                ),
            ),
        ]
    )


async def fetch_all_orders():
    async with make_session() as session:
        result = await session.execute(select(OrderModel))
        rows = result.scalars().all()
        return rows


async def fetch_all_transactions():
    async with make_session() as session:
        result = await session.execute(select(TransactionModel))
        rows = result.scalars().all()
        return rows


async def fetch_all_postings():
    async with make_session() as session:
        result = await session.execute(select(PostingModel))
        rows = result.scalars().all()
        return rows


async def wait_for_orders():
    await sleep(75)


@mark.asyncio
async def test_integration_execute_investment_plan_use_case(
    investment_plan: InvestmentPlan,
    cleanup_all: Any,  # noqa: F811
):
    await execute_investment_plan_use_case.execute(investment_plan)

    await wait_for_orders()

    orders = list(await fetch_all_orders())

    assert len(orders) == 4

    assert orders[0].status == "SUCCESS"
    assert orders[1].status == "SUCCESS"
    assert orders[2].status == "SUCCESS"
    assert orders[3].status == "SUCCESS"

    transactions = list(await fetch_all_transactions())

    assert len(transactions) == 4

    # Check if all transactions are linked to the correct orders regardless of order
    assert all(
        transaction.order_id in [order.id for order in orders]
        for transaction in transactions
    )

    postings = list(await fetch_all_postings())

    assert len(postings) == 8

    # Check if all buy balances are reflected in postings
    assert all(
        transaction.buy_balance_asset_id in [posting.asset_id for posting in postings]
        for transaction in transactions
    )

    # Check if all sell balances are reflected in postings
    assert all(
        transaction.sell_balance_asset_id in [posting.asset_id for posting in postings]
        for transaction in transactions
    )
