from decimal import Decimal
from unittest import mock
from invest_agent.investment.exchange.exchange import Exchange, ConvertedBalance
from invest_agent.investment.investment_parameters import InvestmentParameters
from pytest import fixture, raises, mark
from invest_agent.chain.balance import Balance, BalanceAtomic
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
from protocol.basket import Basket
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
def exchange():
    return mock.Mock(spec=Exchange)


@fixture
def investment_parameters():
    return InvestmentParameters(
        slippage_tolerance_in_percentage=Decimal("1"),
    )


@fixture
def use_case(
    id_generator: IdGenerator,
    date_time: DateTime,
    chain: Chain,
    order_submitter: OrderSubmitter,
    exchange: Exchange,
):
    return ExecuteInvestmentPlanUseCase(
        id_generator,
        date_time,
        chain,
        order_submitter,
        exchange,
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
                    buy_balance=Balance(amount=Decimal(0.5), asset=wbnb_token),
                    sell_balance=Balance(amount=Decimal(0.5), asset=bnb_token),
                ),
                InvestmentPlanStep(
                    buy_balance=Balance(amount=Decimal(0.08), asset=eth_token),
                    sell_balance=Balance(amount=Decimal(0.5), asset=bnb_token),
                ),
            ]
        )
    )

    order_submitter.submit_orders.assert_called_once_with(
        [
            Order(
                id="1",
                sell_balance=BalanceAtomic(
                    amount=Decimal(0.5),
                    amount_atomic=int(0.5 * 10**18),
                    asset=bnb_token,
                ),
                buy_balance=BalanceAtomic(
                    amount=Decimal(0.5),
                    amount_atomic=int(0.5 * 10**18),
                    asset=wbnb_token,
                ),
                type="BUY",
                tries=[],
                created_at=1752268296,
                status="PENDING",
                trigger="MANUAL",
                basket_id=None,
            ),
            Order(
                id="2",
                sell_balance=BalanceAtomic(
                    amount=Decimal(0.5),
                    amount_atomic=int(0.5 * 10**18),
                    asset=bnb_token,
                ),
                buy_balance=BalanceAtomic(
                    amount=Decimal(0.08),
                    amount_atomic=int(0.08 * 10**18),
                    asset=eth_token,
                ),
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
    exchange: Exchange,
    investment_parameters: InvestmentParameters,
    use_case: ExecuteInvestmentPlanUseCase,
):
    date_time.now.return_value = 1752268296
    id_generator.generate_random_id.side_effect = ["1", "2", "3", "4"]

    exchange.convert_balance_to_token.side_effect = [
        ConvertedBalance(
            sell_balance=BalanceAtomic(
                amount=Decimal("0.25"),
                amount_atomic=int(0.25 * 10**18),
                asset=bnb_token,
            ),
            buy_balance=BalanceAtomic(
                amount=Decimal("0.25"),
                amount_atomic=int(0.25 * 10**18),
                asset=wbnb_token,
            ),
        ),
        ConvertedBalance(
            sell_balance=BalanceAtomic(
                amount=Decimal("0.25"),
                amount_atomic=int(0.25 * 10**18),
                asset=bnb_token,
            ),
            buy_balance=BalanceAtomic(
                amount=Decimal("0.10"),
                amount_atomic=int(0.10 * 10**18),
                asset=eth_token,
            ),
        ),
        ConvertedBalance(
            sell_balance=BalanceAtomic(
                amount=Decimal("0.40"),
                amount_atomic=int(0.40 * 10**18),
                asset=bnb_token,
            ),
            buy_balance=BalanceAtomic(
                amount=Decimal("0.30"),
                amount_atomic=int(0.30 * 10**18),
                asset=sol_token,
            ),
        ),
        ConvertedBalance(
            sell_balance=BalanceAtomic(
                amount=Decimal("0.40"),
                amount_atomic=int(0.40 * 10**18),
                asset=bnb_token,
            ),
            buy_balance=BalanceAtomic(
                amount=Decimal("60"), amount_atomic=int(60 * 10**18), asset=usdt_token
            ),
        ),
    ]

    await use_case.execute(
        InvestmentPlan(
            steps=[
                InvestmentPlanStep(
                    buy_balance=Balance(
                        amount=Decimal(1),
                        asset=Basket(
                            id="basket1",
                            name="Basket 1",
                            display_name="Basket 1",
                            ticker="BASK1",
                            description="A sample basket",
                            denomination=Decimal(1),
                            tokens=[wbnb_token, eth_token],
                        ),
                    ),
                    sell_balance=Balance(amount=Decimal("0.5"), asset=bnb_token),
                ),
                InvestmentPlanStep(
                    buy_balance=Balance(
                        amount=Decimal(1),
                        asset=Basket(
                            id="basket2",
                            name="Basket 2",
                            display_name="Basket 2",
                            ticker="BASK2",
                            description="A sample basket",
                            denomination=Decimal(1),
                            tokens=[
                                sol_token,
                                usdt_token,
                            ],
                        ),
                    ),
                    sell_balance=Balance(amount=Decimal("0.80"), asset=bnb_token),
                ),
            ]
        )
    )

    exchange.assert_has_calls(
        [
            mock.call.convert_balance_to_token(
                balance=BalanceAtomic(
                    amount=Decimal("0.25"),
                    amount_atomic=int(0.25 * 10**18),
                    asset=bnb_token,
                ),
                token=wbnb_token,
                investment_parameters=investment_parameters,
            ),
            mock.call.convert_balance_to_token(
                balance=BalanceAtomic(
                    amount=Decimal("0.25"),
                    amount_atomic=int(0.25 * 10**18),
                    asset=bnb_token,
                ),
                token=eth_token,
                investment_parameters=investment_parameters,
            ),
            mock.call.convert_balance_to_token(
                balance=BalanceAtomic(
                    amount=Decimal("0.40"),
                    amount_atomic=int(0.40 * 10**18),
                    asset=bnb_token,
                ),
                token=sol_token,
                investment_parameters=investment_parameters,
            ),
            mock.call.convert_balance_to_token(
                balance=BalanceAtomic(
                    amount=Decimal("0.40"),
                    amount_atomic=int(0.40 * 10**18),
                    asset=bnb_token,
                ),
                token=usdt_token,
                investment_parameters=investment_parameters,
            ),
        ]
    )

    order_submitter.submit_orders.assert_called_once_with(
        [
            Order(
                id="1",
                sell_balance=BalanceAtomic(
                    amount=Decimal("0.25"),
                    amount_atomic=int(0.25 * 10**18),
                    asset=bnb_token,
                ),
                buy_balance=BalanceAtomic(
                    amount=Decimal("0.25"),
                    amount_atomic=int(0.25 * 10**18),
                    asset=wbnb_token,
                ),
                type="BUY",
                tries=[],
                created_at=1752268296,
                status="PENDING",
                trigger="MANUAL",
                basket_id="basket1",
            ),
            Order(
                id="2",
                sell_balance=BalanceAtomic(
                    amount=Decimal("0.25"),
                    amount_atomic=int(0.25 * 10**18),
                    asset=bnb_token,
                ),
                buy_balance=BalanceAtomic(
                    amount=Decimal("0.10"),
                    amount_atomic=int(0.10 * 10**18),
                    asset=eth_token,
                ),
                type="BUY",
                tries=[],
                created_at=1752268296,
                status="PENDING",
                trigger="MANUAL",
                basket_id="basket1",
            ),
            Order(
                id="3",
                sell_balance=BalanceAtomic(
                    amount=Decimal("0.40"),
                    amount_atomic=int(0.40 * 10**18),
                    asset=bnb_token,
                ),
                buy_balance=BalanceAtomic(
                    amount=Decimal("0.30"),
                    amount_atomic=int(0.30 * 10**18),
                    asset=sol_token,
                ),
                type="BUY",
                tries=[],
                created_at=1752268296,
                status="PENDING",
                trigger="MANUAL",
                basket_id="basket2",
            ),
            Order(
                id="4",
                sell_balance=BalanceAtomic(
                    amount=Decimal("0.40"),
                    amount_atomic=int(0.40 * 10**18),
                    asset=bnb_token,
                ),
                buy_balance=BalanceAtomic(
                    amount=Decimal("60"),
                    amount_atomic=int(60 * 10**18),
                    asset=usdt_token,
                ),
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
    exchange: Exchange,
    use_case: ExecuteInvestmentPlanUseCase,
):
    date_time.now.return_value = 1752268296
    id_generator.generate_random_id.side_effect = ["1", "2", "3", "4"]

    exchange.convert_balance_to_token.side_effect = [
        ConvertedBalance(
            sell_balance=BalanceAtomic(
                amount=Decimal("0.25"),
                amount_atomic=int(0.25 * 10**18),
                asset=bnb_token,
            ),
            buy_balance=BalanceAtomic(
                amount=Decimal("0.25"),
                amount_atomic=int(0.25 * 10**18),
                asset=wbnb_token,
            ),
        ),
        ConvertedBalance(
            sell_balance=BalanceAtomic(
                amount=Decimal("0.25"),
                amount_atomic=int(0.25 * 10**18),
                asset=bnb_token,
            ),
            buy_balance=BalanceAtomic(
                amount=Decimal("0.08"),
                amount_atomic=int(0.08 * 10**18),
                asset=eth_token,
            ),
        ),
    ]

    await use_case.execute(
        InvestmentPlan(
            steps=[
                InvestmentPlanStep(
                    buy_balance=Balance(
                        amount=Decimal(1),
                        asset=Basket(
                            id="basket1",
                            name="Basket 1",
                            display_name="Basket 1",
                            ticker="BASK1",
                            description="A sample basket",
                            denomination=Decimal(1),
                            tokens=[
                                wbnb_token,
                                eth_token,
                            ],
                        ),
                    ),
                    sell_balance=Balance(amount=Decimal("0.5"), asset=bnb_token),
                ),
                InvestmentPlanStep(
                    buy_balance=Balance(amount=Decimal("0.5"), asset=wbnb_token),
                    sell_balance=Balance(amount=Decimal("0.5"), asset=bnb_token),
                ),
            ]
        )
    )

    order_submitter.submit_orders.assert_called_once_with(
        [
            Order(
                id="1",
                sell_balance=BalanceAtomic(
                    amount=Decimal("0.25"),
                    amount_atomic=int(0.25 * 10**18),
                    asset=bnb_token,
                ),
                buy_balance=BalanceAtomic(
                    amount=Decimal("0.25"),
                    amount_atomic=int(0.25 * 10**18),
                    asset=wbnb_token,
                ),
                type="BUY",
                tries=[],
                created_at=1752268296,
                status="PENDING",
                trigger="MANUAL",
                basket_id="basket1",
            ),
            Order(
                id="2",
                sell_balance=BalanceAtomic(
                    amount=Decimal("0.25"),
                    amount_atomic=int(0.25 * 10**18),
                    asset=bnb_token,
                ),
                buy_balance=BalanceAtomic(
                    amount=Decimal("0.08"),
                    amount_atomic=int(0.08 * 10**18),
                    asset=eth_token,
                ),
                type="BUY",
                tries=[],
                created_at=1752268296,
                status="PENDING",
                trigger="MANUAL",
                basket_id="basket1",
            ),
            Order(
                id="3",
                sell_balance=BalanceAtomic(
                    amount=Decimal("0.50"),
                    amount_atomic=int(0.50 * 10**18),
                    asset=bnb_token,
                ),
                buy_balance=BalanceAtomic(
                    amount=Decimal("0.50"),
                    amount_atomic=int(0.50 * 10**18),
                    asset=wbnb_token,
                ),
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
                        buy_balance=Balance(
                            amount=Decimal(1),
                            asset=Basket(
                                id="basket1",
                                name="Basket 1",
                                display_name="Basket 1",
                                ticker="BASK1",
                                description="A sample basket",
                                denomination=Decimal(1),
                                tokens=[
                                    eth_token,
                                ],
                            ),
                        ),
                        sell_balance=Balance(
                            amount=Decimal(0.5),
                            asset=Basket(
                                id="basket2",
                                name="Basket 2",
                                display_name="Basket 2",
                                ticker="BASK2",
                                description="A sample basket",
                                denomination=Decimal(1),
                                tokens=[
                                    eth_token,
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
                        asset=bnb_token,
                    ),
                    sell_balance=Balance(
                        amount=Decimal("0.5"),
                        asset=wbnb_token,
                    ),
                ),
                InvestmentPlanStep(
                    buy_balance=Balance(
                        amount=Decimal("0.5"),
                        asset=bnb_token,
                    ),
                    sell_balance=Balance(
                        amount=Decimal("0.08"),
                        asset=eth_token,
                    ),
                ),
            ]
        )
    )

    order_submitter.submit_orders.assert_called_once_with(
        [
            Order(
                id="1",
                sell_balance=BalanceAtomic(
                    amount=Decimal("0.5"),
                    amount_atomic=int(0.5 * 10**18),
                    asset=wbnb_token,
                ),
                buy_balance=BalanceAtomic(
                    amount=Decimal("0.5"),
                    amount_atomic=int(0.5 * 10**18),
                    asset=bnb_token,
                ),
                type="SELL",
                tries=[],
                created_at=1752268296,
                status="PENDING",
                trigger="MANUAL",
                basket_id=None,
            ),
            Order(
                id="2",
                sell_balance=BalanceAtomic(
                    amount=Decimal("0.08"),
                    amount_atomic=int(0.08 * 10**18),
                    asset=eth_token,
                ),
                buy_balance=BalanceAtomic(
                    amount=Decimal("0.5"),
                    amount_atomic=int(0.5 * 10**18),
                    asset=bnb_token,
                ),
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
    exchange: Exchange,
    investment_parameters: InvestmentParameters,
    use_case: ExecuteInvestmentPlanUseCase,
):
    date_time.now.return_value = 1752268296
    id_generator.generate_random_id.side_effect = ["1", "2", "3", "4"]
    exchange.convert_balance_to_token.side_effect = [
        ConvertedBalance(
            sell_balance=BalanceAtomic(
                amount=Decimal("0.25"),
                amount_atomic=int(0.25 * 10**18),
                asset=wbnb_token,
            ),
            buy_balance=BalanceAtomic(
                amount=Decimal("0.25"),
                amount_atomic=int(0.25 * 10**18),
                asset=bnb_token,
            ),
        ),
        ConvertedBalance(
            sell_balance=BalanceAtomic(
                amount=Decimal("0.08"),
                amount_atomic=int(0.08 * 10**18),
                asset=eth_token,
            ),
            buy_balance=BalanceAtomic(
                amount=Decimal("0.25"),
                amount_atomic=int(0.25 * 10**18),
                asset=bnb_token,
            ),
        ),
        ConvertedBalance(
            sell_balance=BalanceAtomic(
                amount=Decimal("0.6"), amount_atomic=int(0.6 * 10**18), asset=sol_token
            ),
            buy_balance=BalanceAtomic(
                amount=Decimal("0.4"), amount_atomic=int(0.4 * 10**18), asset=bnb_token
            ),
        ),
        ConvertedBalance(
            sell_balance=BalanceAtomic(
                amount=Decimal("0.2"), amount_atomic=int(0.2 * 10**18), asset=usdt_token
            ),
            buy_balance=BalanceAtomic(
                amount=Decimal("0.4"), amount_atomic=int(0.4 * 10**18), asset=bnb_token
            ),
        ),
    ]

    await use_case.execute(
        InvestmentPlan(
            steps=[
                InvestmentPlanStep(
                    buy_balance=Balance(amount=Decimal("0.5"), asset=bnb_token),
                    sell_balance=Balance(
                        amount=Decimal(1),
                        asset=Basket(
                            id="basket1",
                            name="Basket 1",
                            display_name="Basket 1",
                            ticker="BASK1",
                            description="A sample basket",
                            denomination=Decimal(1),
                            tokens=[
                                wbnb_token,
                                eth_token,
                            ],
                        ),
                    ),
                ),
                InvestmentPlanStep(
                    buy_balance=Balance(amount=Decimal("0.8"), asset=bnb_token),
                    sell_balance=Balance(
                        amount=Decimal(1),
                        asset=Basket(
                            id="basket2",
                            name="Basket 2",
                            display_name="Basket 2",
                            ticker="BASK2",
                            description="A sample basket",
                            denomination=Decimal(1),
                            tokens=[
                                sol_token,
                                usdt_token,
                            ],
                        ),
                    ),
                ),
            ]
        )
    )

    exchange.assert_has_calls(
        [
            mock.call.convert_balance_to_token(
                balance=BalanceAtomic(
                    amount=Decimal("0"), amount_atomic=0, asset=wbnb_token
                ),
                token=bnb_token,
                investment_parameters=investment_parameters,
            ),
            mock.call.convert_balance_to_token(
                balance=BalanceAtomic(
                    amount=Decimal("0"), amount_atomic=0, asset=eth_token
                ),
                token=bnb_token,
                investment_parameters=investment_parameters,
            ),
            mock.call.convert_balance_to_token(
                balance=BalanceAtomic(
                    amount=Decimal("0"), amount_atomic=0, asset=sol_token
                ),
                token=bnb_token,
                investment_parameters=investment_parameters,
            ),
            mock.call.convert_balance_to_token(
                balance=BalanceAtomic(
                    amount=Decimal("0"), amount_atomic=0, asset=usdt_token
                ),
                token=bnb_token,
                investment_parameters=investment_parameters,
            ),
        ]
    )

    order_submitter.submit_orders.assert_called_once_with(
        [
            Order(
                id="1",
                sell_balance=BalanceAtomic(
                    amount=Decimal("0.25"),
                    amount_atomic=int(0.25 * 10**18),
                    asset=wbnb_token,
                ),
                buy_balance=BalanceAtomic(
                    amount=Decimal("0.25"),
                    amount_atomic=int(0.25 * 10**18),
                    asset=bnb_token,
                ),
                type="SELL",
                tries=[],
                created_at=1752268296,
                status="PENDING",
                trigger="MANUAL",
                basket_id="basket1",
            ),
            Order(
                id="2",
                sell_balance=BalanceAtomic(
                    amount=Decimal("0.08"),
                    amount_atomic=int(0.08 * 10**18),
                    asset=eth_token,
                ),
                buy_balance=BalanceAtomic(
                    amount=Decimal("0.25"),
                    amount_atomic=int(0.25 * 10**18),
                    asset=bnb_token,
                ),
                type="SELL",
                tries=[],
                created_at=1752268296,
                status="PENDING",
                trigger="MANUAL",
                basket_id="basket1",
            ),
            Order(
                id="3",
                sell_balance=BalanceAtomic(
                    amount=Decimal("0.6"),
                    amount_atomic=int(0.6 * 10**18),
                    asset=sol_token,
                ),
                buy_balance=BalanceAtomic(
                    amount=Decimal("0.4"),
                    amount_atomic=int(0.4 * 10**18),
                    asset=bnb_token,
                ),
                type="SELL",
                tries=[],
                created_at=1752268296,
                status="PENDING",
                trigger="MANUAL",
                basket_id="basket2",
            ),
            Order(
                id="4",
                sell_balance=BalanceAtomic(
                    amount=Decimal("0.2"),
                    amount_atomic=int(0.2 * 10**18),
                    asset=usdt_token,
                ),
                buy_balance=BalanceAtomic(
                    amount=Decimal("0.4"),
                    amount_atomic=int(0.4 * 10**18),
                    asset=bnb_token,
                ),
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
    exchange: Exchange,
    use_case: ExecuteInvestmentPlanUseCase,
):
    date_time.now.return_value = 1752268296
    id_generator.generate_random_id.side_effect = ["1", "2", "3", "4"]
    exchange.convert_balance_to_token.side_effect = [
        ConvertedBalance(
            sell_balance=BalanceAtomic(
                amount=Decimal("0.25"),
                amount_atomic=int(0.25 * 10**18),
                asset=wbnb_token,
            ),
            buy_balance=BalanceAtomic(
                amount=Decimal("0.25"),
                amount_atomic=int(0.25 * 10**18),
                asset=bnb_token,
            ),
        ),
        ConvertedBalance(
            sell_balance=BalanceAtomic(
                amount=Decimal("0.10"),
                amount_atomic=int(0.10 * 10**18),
                asset=eth_token,
            ),
            buy_balance=BalanceAtomic(
                amount=Decimal("0.25"),
                amount_atomic=int(0.25 * 10**18),
                asset=bnb_token,
            ),
        ),
    ]

    await use_case.execute(
        InvestmentPlan(
            steps=[
                InvestmentPlanStep(
                    buy_balance=Balance(amount=Decimal("0.5"), asset=bnb_token),
                    sell_balance=Balance(
                        amount=Decimal(1),
                        asset=Basket(
                            id="basket1",
                            name="Basket 1",
                            display_name="Basket 1",
                            ticker="BASK1",
                            description="A sample basket",
                            denomination=Decimal(1),
                            tokens=[
                                wbnb_token,
                                eth_token,
                            ],
                        ),
                    ),
                ),
                InvestmentPlanStep(
                    buy_balance=Balance(amount=Decimal("0.5"), asset=bnb_token),
                    sell_balance=Balance(amount=Decimal("0.5"), asset=wbnb_token),
                ),
            ]
        )
    )

    order_submitter.submit_orders.assert_called_once_with(
        [
            Order(
                id="1",
                sell_balance=BalanceAtomic(
                    amount=Decimal("0.25"),
                    amount_atomic=int(0.25 * 10**18),
                    asset=wbnb_token,
                ),
                buy_balance=BalanceAtomic(
                    amount=Decimal("0.25"),
                    amount_atomic=int(0.25 * 10**18),
                    asset=bnb_token,
                ),
                type="SELL",
                tries=[],
                created_at=1752268296,
                status="PENDING",
                trigger="MANUAL",
                basket_id="basket1",
            ),
            Order(
                id="2",
                sell_balance=BalanceAtomic(
                    amount=Decimal("0.10"),
                    amount_atomic=int(0.10 * 10**18),
                    asset=eth_token,
                ),
                buy_balance=BalanceAtomic(
                    amount=Decimal("0.25"),
                    amount_atomic=int(0.25 * 10**18),
                    asset=bnb_token,
                ),
                type="SELL",
                tries=[],
                created_at=1752268296,
                status="PENDING",
                trigger="MANUAL",
                basket_id="basket1",
            ),
            Order(
                id="3",
                sell_balance=BalanceAtomic(
                    amount=Decimal("0.5"),
                    amount_atomic=int(0.5 * 10**18),
                    asset=wbnb_token,
                ),
                buy_balance=BalanceAtomic(
                    amount=Decimal("0.5"),
                    amount_atomic=int(0.5 * 10**18),
                    asset=bnb_token,
                ),
                type="SELL",
                tries=[],
                created_at=1752268296,
                status="PENDING",
                trigger="MANUAL",
                basket_id=None,
            ),
        ]
    )
