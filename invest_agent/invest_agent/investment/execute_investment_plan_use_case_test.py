from decimal import Decimal
from unittest import mock
from invest_agent.chain.asset_balance import (
    BasketBalance,
    TokenBalance,
)
from invest_agent.chain.balance import Balance
from invest_agent.chain.chain import Chain
from invest_agent.datetime.date_time import DateTime
from invest_agent.investment.exception.cannot_swap_basket_for_another_exception import (
    CannotSwapBasketForAnotherException,
)
from invest_agent.investment.execute_investment_plan_use_case import (
    ExecuteInvestmentPlanUseCase,
)

from invest_agent.investment.investment_planner.investment_plan import (
    InvestmentPlan,
    InvestmentPlanStep,
)
from invest_agent.investment.order.order import Order
from invest_agent.investment.order.order_submitter import OrderSubmitter
from pytest import fixture, raises, mark
from protocol.fixture.token import (
    bnb_token,
    wbnb_token,
    eth_token,
    sol_token,
    usdt_token,
)
from shared.id_generator.id_generator import IdGenerator


@fixture
def id_generator():
    return mock.Mock(spec=IdGenerator)


@fixture
def date_time():
    return mock.Mock(spec=DateTime)


@fixture
def chain():
    chain = mock.Mock(spec=Chain)

    chain.get_base_token.return_value = bnb_token

    return chain


@fixture
def order_submitter():
    return mock.Mock(spec=OrderSubmitter)


@fixture
def use_case(
    id_generator: IdGenerator,
    date_time: DateTime,
    chain: Chain,
    order_submitter: OrderSubmitter,
):
    return ExecuteInvestmentPlanUseCase(
        id_generator,
        date_time,
        chain,
        order_submitter,
    )


@mark.asyncio
async def test_execute_investment_plan_use_case_buy_only_tokens(
    id_generator: IdGenerator,
    date_time: DateTime,
    order_submitter: OrderSubmitter,
    use_case: ExecuteInvestmentPlanUseCase,
):
    date_time.now.return_value = 1752268296
    id_generator.generate_random_id.side_effect = ["1", "2"]

    await use_case.execute(
        InvestmentPlan(
            steps=[
                InvestmentPlanStep(
                    buy_balance=Balance(amount=Decimal(0.5), token=wbnb_token),
                    sell_balance=Balance(amount=Decimal(0.5), token=bnb_token),
                ),
                InvestmentPlanStep(
                    buy_balance=Balance(amount=Decimal(0.08), token=eth_token),
                    sell_balance=Balance(amount=Decimal(0.5), token=bnb_token),
                ),
            ]
        )
    )

    order_submitter.submit_orders.assert_called_once_with(
        [
            Order(
                id="1",
                sell_balance=Balance(amount=Decimal(0.5), token=bnb_token),
                buy_balance=Balance(amount=Decimal(0.5), token=wbnb_token),
                type="BUY",
                tries=[],
                created_at=1752268296,
                status="PENDING",
                trigger="MANUAL",
                basket_id=None,
            ),
            Order(
                id="2",
                sell_balance=Balance(amount=Decimal(0.5), token=bnb_token),
                buy_balance=Balance(amount=Decimal(0.08), token=eth_token),
                type="BUY",
                tries=[],
                created_at=1752268296,
                status="PENDING",
                trigger="MANUAL",
                basket_id=None,
            ),
        ]
    )


@mark.asyncio
async def test_execute_investment_plan_use_case_buy_only_baskets(
    id_generator: IdGenerator,
    date_time: DateTime,
    order_submitter: OrderSubmitter,
    use_case: ExecuteInvestmentPlanUseCase,
):
    date_time.now.return_value = 1752268296
    id_generator.generate_random_id.side_effect = ["1", "2", "3", "4"]

    await use_case.execute(
        InvestmentPlan(
            steps=[
                InvestmentPlanStep(
                    buy_balance=BasketBalance(
                        amount=Decimal(1),
                        basket=BasketWithTokenBalances(
                            id="basket1",
                            name="Basket 1",
                            description="A sample basket",
                            denomination=Decimal(1),
                            balances=[
                                TokenBalance(
                                    sell_balance=Balance(
                                        amount=Decimal("0.25"), token=bnb_token
                                    ),
                                    buy_balance=Balance(
                                        amount=Decimal("0.25"), token=wbnb_token
                                    ),
                                ),
                                TokenBalance(
                                    sell_balance=Balance(
                                        amount=Decimal("0.25"), token=bnb_token
                                    ),
                                    buy_balance=Balance(
                                        amount=Decimal("0.10"), token=eth_token
                                    ),
                                ),
                            ],
                        ),
                    ),
                    sell_balance=Balance(amount=Decimal("0.5"), token=bnb_token),
                ),
                InvestmentPlanStep(
                    buy_balance=BasketBalance(
                        amount=Decimal(1),
                        basket=BasketWithTokenBalances(
                            id="basket2",
                            name="Basket 2",
                            description="A sample basket",
                            denomination=Decimal(1),
                            balances=[
                                TokenBalance(
                                    sell_balance=Balance(
                                        amount=Decimal("0.40"), token=bnb_token
                                    ),
                                    buy_balance=Balance(
                                        amount=Decimal("0.30"), token=sol_token
                                    ),
                                ),
                                TokenBalance(
                                    sell_balance=Balance(
                                        amount=Decimal("0.40"), token=bnb_token
                                    ),
                                    buy_balance=Balance(
                                        amount=Decimal("60"), token=usdt_token
                                    ),
                                ),
                            ],
                        ),
                    ),
                    sell_balance=Balance(amount=Decimal("0.80"), token=bnb_token),
                ),
            ]
        )
    )

    order_submitter.submit_orders.assert_called_once_with(
        [
            Order(
                id="1",
                sell_balance=Balance(amount=Decimal("0.25"), token=bnb_token),
                buy_balance=Balance(amount=Decimal("0.25"), token=wbnb_token),
                type="BUY",
                tries=[],
                created_at=1752268296,
                status="PENDING",
                trigger="MANUAL",
                basket_id="basket1",
            ),
            Order(
                id="2",
                sell_balance=Balance(amount=Decimal("0.25"), token=bnb_token),
                buy_balance=Balance(amount=Decimal("0.10"), token=eth_token),
                type="BUY",
                tries=[],
                created_at=1752268296,
                status="PENDING",
                trigger="MANUAL",
                basket_id="basket1",
            ),
            Order(
                id="3",
                sell_balance=Balance(amount=Decimal("0.40"), token=bnb_token),
                buy_balance=Balance(amount=Decimal("0.30"), token=sol_token),
                type="BUY",
                tries=[],
                created_at=1752268296,
                status="PENDING",
                trigger="MANUAL",
                basket_id="basket2",
            ),
            Order(
                id="4",
                sell_balance=Balance(amount=Decimal("0.40"), token=bnb_token),
                buy_balance=Balance(amount=Decimal("60"), token=usdt_token),
                type="BUY",
                tries=[],
                created_at=1752268296,
                status="PENDING",
                trigger="MANUAL",
                basket_id="basket2",
            ),
        ]
    )


@mark.asyncio
async def test_execute_investment_plan_use_case_buy_token_and_basket(
    id_generator: IdGenerator,
    date_time: DateTime,
    order_submitter: OrderSubmitter,
    use_case: ExecuteInvestmentPlanUseCase,
):
    date_time.now.return_value = 1752268296
    id_generator.generate_random_id.side_effect = ["1", "2", "3", "4"]

    await use_case.execute(
        InvestmentPlan(
            steps=[
                InvestmentPlanStep(
                    buy_balance=BasketBalance(
                        amount=Decimal(1),
                        basket=BasketWithTokenBalances(
                            id="basket1",
                            name="Basket 1",
                            description="A sample basket",
                            denomination=Decimal(1),
                            balances=[
                                TokenBalance(
                                    sell_balance=Balance(
                                        amount=Decimal("0.25"),
                                        token=bnb_token,
                                    ),
                                    buy_balance=Balance(
                                        amount=Decimal("0.25"),
                                        token=wbnb_token,
                                    ),
                                ),
                                TokenBalance(
                                    sell_balance=Balance(
                                        amount=Decimal("0.25"),
                                        token=bnb_token,
                                    ),
                                    buy_balance=Balance(
                                        amount=Decimal("0.08"),
                                        token=eth_token,
                                    ),
                                ),
                            ],
                        ),
                    ),
                    sell_balance=Balance(amount=Decimal("0.5"), token=bnb_token),
                ),
                InvestmentPlanStep(
                    buy_balance=Balance(amount=Decimal("0.5"), token=wbnb_token),
                    sell_balance=Balance(amount=Decimal("0.5"), token=bnb_token),
                ),
            ]
        )
    )

    order_submitter.submit_orders.assert_called_once_with(
        [
            Order(
                id="1",
                sell_balance=Balance(amount=Decimal("0.25"), token=bnb_token),
                buy_balance=Balance(amount=Decimal("0.25"), token=wbnb_token),
                type="BUY",
                tries=[],
                created_at=1752268296,
                status="PENDING",
                trigger="MANUAL",
                basket_id="basket1",
            ),
            Order(
                id="2",
                sell_balance=Balance(amount=Decimal("0.25"), token=bnb_token),
                buy_balance=Balance(amount=Decimal("0.08"), token=eth_token),
                type="BUY",
                tries=[],
                created_at=1752268296,
                status="PENDING",
                trigger="MANUAL",
                basket_id="basket1",
            ),
            Order(
                id="3",
                sell_balance=Balance(amount=Decimal("0.50"), token=bnb_token),
                buy_balance=Balance(amount=Decimal("0.50"), token=wbnb_token),
                type="BUY",
                tries=[],
                created_at=1752268296,
                status="PENDING",
                trigger="MANUAL",
                basket_id=None,
            ),
        ]
    )


@mark.asyncio
async def test_execute_investment_plan_use_case_buy_basket_sell_basket(
    id_generator: IdGenerator,
    date_time: DateTime,
    use_case: ExecuteInvestmentPlanUseCase,
):
    date_time.now.return_value = 1752268296
    id_generator.generate_random_id.side_effect = ["1", "2", "3", "4"]

    with raises(CannotSwapBasketForAnotherException):
        await use_case.execute(
            InvestmentPlan(
                steps=[
                    InvestmentPlanStep(
                        buy_balance=BasketBalance(
                            amount=Decimal(1),
                            basket=BasketWithTokenBalances(
                                id="basket1",
                                name="Basket 1",
                                description="A sample basket",
                                denomination=Decimal(1),
                                balances=[
                                    TokenBalance(
                                        sell_balance=Balance(
                                            amount=Decimal("0.25"), token=wbnb_token
                                        ),
                                        buy_balance=Balance(
                                            amount=Decimal("0.08"), token=eth_token
                                        ),
                                    ),
                                ],
                            ),
                        ),
                        sell_balance=BasketBalance(
                            amount=Decimal(0.5),
                            basket=BasketWithTokenBalances(
                                id="basket2",
                                name="Basket 2",
                                description="A sample basket",
                                denomination=Decimal(1),
                                balances=[
                                    TokenBalance(
                                        sell_balance=Balance(
                                            amount=Decimal("0.25"), token=wbnb_token
                                        ),
                                        buy_balance=Balance(
                                            amount=Decimal("0.08"), token=eth_token
                                        ),
                                    ),
                                ],
                            ),
                        ),
                    ),
                ]
            )
        )


@mark.asyncio
async def test_execute_investment_plan_use_case_sell_only_tokens(
    id_generator: IdGenerator,
    date_time: DateTime,
    order_submitter: OrderSubmitter,
    use_case: ExecuteInvestmentPlanUseCase,
):
    date_time.now.return_value = 1752268296
    id_generator.generate_random_id.side_effect = ["1", "2"]

    await use_case.execute(
        InvestmentPlan(
            steps=[
                InvestmentPlanStep(
                    buy_balance=Balance(
                        amount=Decimal("0.5"),
                        token=bnb_token,
                    ),
                    sell_balance=Balance(
                        amount=Decimal("0.5"),
                        token=wbnb_token,
                    ),
                ),
                InvestmentPlanStep(
                    buy_balance=Balance(
                        amount=Decimal("0.5"),
                        token=bnb_token,
                    ),
                    sell_balance=Balance(
                        amount=Decimal("0.08"),
                        token=eth_token,
                    ),
                ),
            ]
        )
    )

    order_submitter.submit_orders.assert_called_once_with(
        [
            Order(
                id="1",
                sell_balance=Balance(amount=Decimal("0.5"), token=wbnb_token),
                buy_balance=Balance(amount=Decimal("0.5"), token=bnb_token),
                type="SELL",
                tries=[],
                created_at=1752268296,
                status="PENDING",
                trigger="MANUAL",
                basket_id=None,
            ),
            Order(
                id="2",
                sell_balance=Balance(amount=Decimal("0.08"), token=eth_token),
                buy_balance=Balance(amount=Decimal("0.5"), token=bnb_token),
                type="SELL",
                tries=[],
                created_at=1752268296,
                status="PENDING",
                trigger="MANUAL",
                basket_id=None,
            ),
        ]
    )


@mark.asyncio
async def test_execute_investment_plan_use_case_sell_only_baskets(
    id_generator: IdGenerator,
    date_time: DateTime,
    order_submitter: OrderSubmitter,
    use_case: ExecuteInvestmentPlanUseCase,
):
    date_time.now.return_value = 1752268296
    id_generator.generate_random_id.side_effect = ["1", "2", "3", "4"]

    await use_case.execute(
        InvestmentPlan(
            steps=[
                InvestmentPlanStep(
                    buy_balance=Balance(amount=Decimal("0.5"), token=bnb_token),
                    sell_balance=BasketBalance(
                        amount=Decimal(1),
                        basket=BasketWithTokenBalances(
                            id="basket1",
                            name="Basket 1",
                            description="A sample basket",
                            denomination=Decimal(1),
                            balances=[
                                TokenBalance(
                                    sell_balance=Balance(
                                        amount=Decimal("0.25"), token=wbnb_token
                                    ),
                                    buy_balance=Balance(
                                        amount=Decimal("0.25"), token=bnb_token
                                    ),
                                ),
                                TokenBalance(
                                    sell_balance=Balance(
                                        amount=Decimal("0.08"), token=eth_token
                                    ),
                                    buy_balance=Balance(
                                        amount=Decimal("0.25"), token=bnb_token
                                    ),
                                ),
                            ],
                        ),
                    ),
                ),
                InvestmentPlanStep(
                    buy_balance=Balance(amount=Decimal("0.8"), token=bnb_token),
                    sell_balance=BasketBalance(
                        amount=Decimal(1),
                        basket=BasketWithTokenBalances(
                            id="basket2",
                            name="Basket 2",
                            description="A sample basket",
                            denomination=Decimal(1),
                            balances=[
                                TokenBalance(
                                    sell_balance=Balance(
                                        amount=Decimal("0.6"), token=sol_token
                                    ),
                                    buy_balance=Balance(
                                        amount=Decimal("0.4"), token=bnb_token
                                    ),
                                ),
                                TokenBalance(
                                    sell_balance=Balance(
                                        amount=Decimal("0.2"), token=usdt_token
                                    ),
                                    buy_balance=Balance(
                                        amount=Decimal("0.4"), token=bnb_token
                                    ),
                                ),
                            ],
                        ),
                    ),
                ),
            ]
        )
    )

    order_submitter.submit_orders.assert_called_once_with(
        [
            Order(
                id="1",
                sell_balance=Balance(amount=Decimal("0.25"), token=wbnb_token),
                buy_balance=Balance(amount=Decimal("0.25"), token=bnb_token),
                type="SELL",
                tries=[],
                created_at=1752268296,
                status="PENDING",
                trigger="MANUAL",
                basket_id="basket1",
            ),
            Order(
                id="2",
                sell_balance=Balance(amount=Decimal("0.08"), token=eth_token),
                buy_balance=Balance(amount=Decimal("0.25"), token=bnb_token),
                type="SELL",
                tries=[],
                created_at=1752268296,
                status="PENDING",
                trigger="MANUAL",
                basket_id="basket1",
            ),
            Order(
                id="3",
                sell_balance=Balance(amount=Decimal("0.6"), token=sol_token),
                buy_balance=Balance(amount=Decimal("0.4"), token=bnb_token),
                type="SELL",
                tries=[],
                created_at=1752268296,
                status="PENDING",
                trigger="MANUAL",
                basket_id="basket2",
            ),
            Order(
                id="4",
                sell_balance=Balance(amount=Decimal("0.2"), token=usdt_token),
                buy_balance=Balance(amount=Decimal("0.4"), token=bnb_token),
                type="SELL",
                tries=[],
                created_at=1752268296,
                status="PENDING",
                trigger="MANUAL",
                basket_id="basket2",
            ),
        ]
    )


@mark.asyncio
async def test_execute_investment_plan_use_case_sell_token_and_basket(
    id_generator: IdGenerator,
    date_time: DateTime,
    order_submitter: OrderSubmitter,
    use_case: ExecuteInvestmentPlanUseCase,
):
    date_time.now.return_value = 1752268296
    id_generator.generate_random_id.side_effect = ["1", "2", "3", "4"]

    await use_case.execute(
        InvestmentPlan(
            steps=[
                InvestmentPlanStep(
                    buy_balance=Balance(amount=Decimal("0.5"), token=bnb_token),
                    sell_balance=BasketBalance(
                        amount=Decimal(1),
                        basket=BasketWithTokenBalances(
                            id="basket1",
                            name="Basket 1",
                            description="A sample basket",
                            denomination=Decimal(1),
                            balances=[
                                TokenBalance(
                                    sell_balance=Balance(
                                        amount=Decimal("0.25"), token=wbnb_token
                                    ),
                                    buy_balance=Balance(
                                        amount=Decimal("0.25"), token=bnb_token
                                    ),
                                ),
                                TokenBalance(
                                    sell_balance=Balance(
                                        amount=Decimal("0.10"), token=eth_token
                                    ),
                                    buy_balance=Balance(
                                        amount=Decimal("0.25"), token=bnb_token
                                    ),
                                ),
                            ],
                        ),
                    ),
                ),
                InvestmentPlanStep(
                    buy_balance=Balance(amount=Decimal("0.5"), token=bnb_token),
                    sell_balance=Balance(amount=Decimal("0.5"), token=wbnb_token),
                ),
            ]
        )
    )

    order_submitter.submit_orders.assert_called_once_with(
        [
            Order(
                id="1",
                sell_balance=Balance(amount=Decimal("0.25"), token=wbnb_token),
                buy_balance=Balance(amount=Decimal("0.25"), token=bnb_token),
                type="SELL",
                tries=[],
                created_at=1752268296,
                status="PENDING",
                trigger="MANUAL",
                basket_id="basket1",
            ),
            Order(
                id="2",
                sell_balance=Balance(amount=Decimal("0.10"), token=eth_token),
                buy_balance=Balance(amount=Decimal("0.25"), token=bnb_token),
                type="SELL",
                tries=[],
                created_at=1752268296,
                status="PENDING",
                trigger="MANUAL",
                basket_id="basket1",
            ),
            Order(
                id="3",
                sell_balance=Balance(amount=Decimal("0.5"), token=wbnb_token),
                buy_balance=Balance(amount=Decimal("0.5"), token=bnb_token),
                type="SELL",
                tries=[],
                created_at=1752268296,
                status="PENDING",
                trigger="MANUAL",
                basket_id=None,
            ),
        ]
    )
