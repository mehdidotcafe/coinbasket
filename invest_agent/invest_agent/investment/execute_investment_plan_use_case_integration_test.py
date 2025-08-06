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
from invest_agent.chain.asset_balance import (
    BasketWithTokenBalances,
    BasketBalance,
    TokenBalance,
)
from sqlalchemy import select

from invest_agent.test.database.make_session import make_session
from invest_agent.test.database.cleanup_all import cleanup_all


@fixture
def investment_plan():
    return InvestmentPlan(
        steps=[
            InvestmentPlanStep(
                buy_balance=BasketBalance(
                    amount=Decimal("1"),
                    basket=BasketWithTokenBalances(
                        id="c0e724d3-c4d0-4bd0-973d-edd3907ecf51",
                        name="Memecoin Mania",
                        description="A basket of popular memecoins",
                        denomination=Decimal("1"),
                        balances=[
                            TokenBalance(
                                buy_balance=Balance(
                                    token=Token(
                                        id="bsc:0xbA2aE424d960c26247Dd6c32edC70B295c744C43",
                                        name="Dogecoin",
                                        display_name="Dogecoin",
                                        ticker="DOGE",
                                        address="0xbA2aE424d960c26247Dd6c32edC70B295c744C43",
                                    ),
                                    amount=Decimal("1000"),
                                ),
                                sell_balance=Balance(
                                    token=Token(
                                        id="bsc:0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                                        name="Binance Coin",
                                        display_name="Binance Coin",
                                        ticker="BNB",
                                        address="0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                                    ),
                                    amount=Decimal("1"),
                                ),
                            ),
                            TokenBalance(
                                buy_balance=Balance(
                                    token=Token(
                                        id="bsc:0x2859e4544C4bB03966803b044A93563Bd2D0DD4D",
                                        name="SHIBA INU",
                                        display_name="Shiba Inu",
                                        ticker="SHIB",
                                        address="0x2859e4544C4bB03966803b044A93563Bd2D0DD4D",
                                    ),
                                    amount=Decimal("1000000"),
                                ),
                                sell_balance=Balance(
                                    token=Token(
                                        id="bsc:0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                                        name="Binance Coin",
                                        display_name="Binance Coin",
                                        ticker="BNB",
                                        address="0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                                    ),
                                    amount=Decimal("1"),
                                ),
                            ),
                            TokenBalance(
                                buy_balance=Balance(
                                    token=Token(
                                        id="bsc:0x25d887Ce7a35172C62FeBFD67a1856F20FaEbB00",
                                        name="Pepe",
                                        display_name="Pepe",
                                        ticker="PEPE",
                                        address="0x25d887Ce7a35172C62FeBFD67a1856F20FaEbB00",
                                    ),
                                    amount=Decimal("1000000"),
                                ),
                                sell_balance=Balance(
                                    token=Token(
                                        id="bsc:0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                                        name="Binance Coin",
                                        display_name="Binance Coin",
                                        ticker="BNB",
                                        address="0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                                    ),
                                    amount=Decimal("1"),
                                ),
                            ),
                            TokenBalance(
                                buy_balance=Balance(
                                    token=Token(
                                        id="bsc:0xfb5b838b6cfeedc2873ab27866079ac55363d37e",
                                        name="FLOKI",
                                        display_name="FLOKI",
                                        ticker="FLOKI",
                                        address="0xfb5b838b6cfeedc2873ab27866079ac55363d37e",
                                    ),
                                    amount=Decimal("1000000"),
                                ),
                                sell_balance=Balance(
                                    token=Token(
                                        id="bsc:0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                                        name="Binance Coin",
                                        display_name="Binance Coin",
                                        ticker="BNB",
                                        address="0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                                    ),
                                    amount=Decimal("1"),
                                ),
                            ),
                            TokenBalance(
                                buy_balance=Balance(
                                    token=Token(
                                        id="bsc:0xA697e272a73744b343528C3Bc4702F2565b2F422",
                                        name="Bonk",
                                        display_name="Bonk",
                                        ticker="BONK",
                                        address="0xA697e272a73744b343528C3Bc4702F2565b2F422",
                                    ),
                                    amount=Decimal("1000000"),
                                ),
                                sell_balance=Balance(
                                    token=Token(
                                        id="bsc:0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                                        name="Binance Coin",
                                        display_name="Binance Coin",
                                        ticker="BNB",
                                        address="0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                                    ),
                                    amount=Decimal("1"),
                                ),
                            ),
                            TokenBalance(
                                buy_balance=Balance(
                                    token=Token(
                                        id="bsc:0x86Bb94DdD16Efc8bc58e6b056e8df71D9e666429",
                                        name="Test",
                                        display_name="Test",
                                        ticker="TST",
                                        address="0x86Bb94DdD16Efc8bc58e6b056e8df71D9e666429",
                                    ),
                                    amount=Decimal("1000000"),
                                ),
                                sell_balance=Balance(
                                    token=Token(
                                        id="bsc:0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                                        name="Binance Coin",
                                        display_name="Binance Coin",
                                        ticker="BNB",
                                        address="0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                                    ),
                                    amount=Decimal("1"),
                                ),
                            ),
                            TokenBalance(
                                buy_balance=Balance(
                                    token=Token(
                                        id="bsc:0x5C85D6C6825aB4032337F11Ee92a72DF936b46F6",
                                        name="mubarak",
                                        display_name="mubarak",
                                        ticker="MUBARAK",
                                        address="0x5C85D6C6825aB4032337F11Ee92a72DF936b46F6",
                                    ),
                                    amount=Decimal("100"),
                                ),
                                sell_balance=Balance(
                                    token=Token(
                                        id="bsc:0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                                        name="Binance Coin",
                                        display_name="Binance Coin",
                                        ticker="BNB",
                                        address="0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                                    ),
                                    amount=Decimal("1"),
                                ),
                            ),
                        ],
                    ),
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
