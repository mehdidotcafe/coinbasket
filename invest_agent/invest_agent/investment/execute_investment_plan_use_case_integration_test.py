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
from pytest import fixture, mark

from invest_agent.main import (
    execute_investment_plan_use_case,
)
from invest_agent.investment.investment_planner.investment_plan import (
    InvestmentPlan,
    InvestmentPlanStep,
)
from protocol.token import Token
from protocol.fixture.basket import (
    memecoinmania_basket,
)
from invest_agent.chain.asset_balance import (
    BasketBalance,
)
from sqlalchemy import select

from invest_agent.test.database.make_session import make_session


@fixture
def investment_plan():
    return InvestmentPlan(
        steps=[
            InvestmentPlanStep(
                buy_balance=BasketBalance(
                    amount=Decimal("1"),
                    basket=memecoinmania_basket,
                ),
                sell_balance=Balance(
                    token=Token(
                        id="bsc:0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                        name="Binance Coin",
                        display_name="Binance Coin",
                        ticker="BNB",
                        address="0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                    ),
                    amount=Decimal("7"),
                ),
            ),
            InvestmentPlanStep(
                buy_balance=Balance(
                    token=Token(
                        id="bsc:0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
                        name="Bitcoin",
                        display_name="Bitcoin",
                        ticker="BTC",
                        address="0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
                    ),
                    amount=Decimal("0.001"),
                ),
                sell_balance=Balance(
                    token=Token(
                        id="bsc:0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                        name="Binance Coin",
                        display_name="Binance Coin",
                        ticker="BNB",
                        address="0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                    ),
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


async def wait_for_orders():
    await sleep(75)


@mark.asyncio
async def test_integration_execute_investment_plan_use_case(
    investment_plan: InvestmentPlan,
    cleanup_all: Any,
):
    await execute_investment_plan_use_case.execute(investment_plan)

    await wait_for_orders()

    orders = list(await fetch_all_orders())

    assert len(orders) == 8

    assert orders[0].status == "SUCCESS"
    assert orders[1].status == "SUCCESS"
    assert orders[2].status == "SUCCESS"
    assert orders[3].status == "SUCCESS"
    assert orders[4].status == "SUCCESS"
    assert orders[5].status == "SUCCESS"
    assert orders[6].status == "SUCCESS"
    assert orders[7].status == "SUCCESS"

    transactions = list(await fetch_all_transactions())

    assert len(transactions) == 8

    # Check if all transactions are linked to the correct orders regardless of order
    assert all(
        transaction.order_id in [order.id for order in orders]
        for transaction in transactions
    )
