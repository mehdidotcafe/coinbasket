from decimal import ROUND_DOWN, Decimal
from unittest import mock
from api.investment.calculator.asset_balance_converter import (
    AssetBalanceConverter,
)
from api.investment.exception.insufficient_asset_balance import (
    InsufficientAssetBalance,
)
from api.investment.exchange.exchange import Exchange, ExchangeConvertedBalance
from api.investment.investment_parameters import InvestmentParameters
from api.portfolio.posting.posting_repository import PostingRepository
from pytest import fixture, raises, mark
from api.chain.balance import Balance, BalanceAtomic
from api.chain.chain import Chain
from api.datetime.date_time import DateTime
from api.investment.exception.cannot_swap_basket_for_another_exception import (
    CannotSwapBasketForAnotherException,
)
from api.investment.execute_investment_plan_use_case import (
    ExecuteInvestmentPlanUseCase,
)

from api.investment.investment_planner.investment_plan import (
    InvestmentPlan,
    InvestmentPlanStep,
)
from api.investment.order.order import Order
from api.investment.order.order_submitter import OrderSubmitter
from api.protocol.basket import Basket
from api.protocol.fixture.token import (
    bnb_token,
    wbnb_token,
    eth_token,
    sol_token,
    usdt_token,
)
from api.shared.id_generator.id_generator import IdGenerator
from api.portfolio.holding.holding import Holding


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
    chain.convert_amount_to_amount_atomic.side_effect = lambda token, amount_readable: (
        int(
            (Decimal(amount_readable) * (10**18)).to_integral_exact(rounding=ROUND_DOWN)
        ),
        18,
    )
    chain.convert_amount_atomic_to_amount.side_effect = lambda token, amount_atomic: (
        int((Decimal(amount_atomic) / (10**18)).to_integral_exact(rounding=ROUND_DOWN)),
        18,
    )

    return chain


@fixture
def order_submitter():
    return mock.Mock(spec=OrderSubmitter)


@fixture
def exchange():
    return mock.Mock(spec=Exchange)


@fixture
def posting_repository():
    return mock.Mock(spec=PostingRepository)


@fixture
def asset_balance_converter():
    return mock.Mock(spec=AssetBalanceConverter)


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
    posting_repository: PostingRepository,
    asset_balance_converter: AssetBalanceConverter,
):
    return ExecuteInvestmentPlanUseCase(
        id_generator,
        date_time,
        chain,
        order_submitter,
        exchange,
        posting_repository,
        asset_balance_converter,
    )


@mark.asyncio
async def test_execute_investment_plan_use_case_not_enough_holdings(
    posting_repository: PostingRepository,
    chain: Chain,
    use_case: ExecuteInvestmentPlanUseCase,
):
    posting_repository.get_holding_balances.return_value = [
        Holding(
            balance=BalanceAtomic(
                amount=Decimal("0.75"),
                amount_atomic=75 * 10**16,
                decimals=18,
                asset=eth_token,
            ),
            children=None,
        ),
    ]
    chain.get_native_token_balance.return_value = BalanceAtomic(
        amount=Decimal("0"),
        amount_atomic=0,
        decimals=18,
        asset=bnb_token,
    )

    with raises(InsufficientAssetBalance):
        await use_case.execute(
            InvestmentPlan(
                steps=[
                    InvestmentPlanStep(
                        buy_balance=Balance(amount=Decimal("0.5"), asset=wbnb_token),
                        sell_balance=Balance(amount=Decimal("0.5"), asset=eth_token),
                    ),
                    InvestmentPlanStep(
                        buy_balance=Balance(amount=Decimal("0.08"), asset=eth_token),
                        sell_balance=Balance(amount=Decimal("0.5"), asset=eth_token),
                    ),
                ]
            )
        )


@mark.asyncio
async def test_execute_investment_plan_use_case_not_enough_available_balance(
    posting_repository: PostingRepository,
    chain: Chain,
    use_case: ExecuteInvestmentPlanUseCase,
):
    posting_repository.get_holding_balances.return_value = []
    chain.get_native_token_balance.return_value = BalanceAtomic(
        amount=Decimal("0.75"),
        amount_atomic=75 * 10**16,
        decimals=18,
        asset=bnb_token,
    )

    with raises(InsufficientAssetBalance):
        await use_case.execute(
            InvestmentPlan(
                steps=[
                    InvestmentPlanStep(
                        buy_balance=Balance(amount=Decimal("0.5"), asset=wbnb_token),
                        sell_balance=Balance(amount=Decimal("0.5"), asset=bnb_token),
                    ),
                    InvestmentPlanStep(
                        buy_balance=Balance(amount=Decimal("0.08"), asset=eth_token),
                        sell_balance=Balance(amount=Decimal("0.5"), asset=bnb_token),
                    ),
                ]
            )
        )


@mark.asyncio
async def test_execute_investment_plan_use_case_empty_sell_balance(
    order_submitter: OrderSubmitter,
    chain: Chain,
    posting_repository: PostingRepository,
    use_case: ExecuteInvestmentPlanUseCase,
):
    posting_repository.get_holding_balances.return_value = []
    chain.get_native_token_balance.return_value = BalanceAtomic(
        amount=Decimal("75"),
        amount_atomic=75 * 10**18,
        decimals=18,
        asset=bnb_token,
    )

    orders = await use_case.execute(
        InvestmentPlan(
            steps=[
                InvestmentPlanStep(
                    buy_balance=Balance(amount=Decimal("0.5"), asset=wbnb_token),
                    sell_balance=Balance(amount=Decimal("0"), asset=bnb_token),
                ),
            ]
        )
    )

    order_submitter.submit_orders.assert_not_called()

    assert len(orders) == 0


@mark.asyncio
async def test_execute_investment_plan_use_case_buy_only_tokens(
    id_generator: IdGenerator,
    date_time: DateTime,
    order_submitter: OrderSubmitter,
    chain: Chain,
    posting_repository: PostingRepository,
    use_case: ExecuteInvestmentPlanUseCase,
):
    date_time.now.return_value = 1752268296
    id_generator.generate_random_id.side_effect = ["1", "2"]
    posting_repository.get_holding_balances.return_value = []
    chain.get_native_token_balance.return_value = BalanceAtomic(
        amount=Decimal("75"),
        amount_atomic=75 * 10**18,
        decimals=18,
        asset=bnb_token,
    )

    await use_case.execute(
        InvestmentPlan(
            steps=[
                InvestmentPlanStep(
                    buy_balance=Balance(amount=Decimal("0.5"), asset=wbnb_token),
                    sell_balance=Balance(amount=Decimal("0.5"), asset=bnb_token),
                ),
                InvestmentPlanStep(
                    buy_balance=Balance(amount=Decimal("0.08"), asset=eth_token),
                    sell_balance=Balance(amount=Decimal("0.5"), asset=bnb_token),
                ),
            ]
        )
    )

    order_submitter.submit_orders.assert_called_once_with(
        [
            [
                Order(
                    id="1",
                    sell_balance=BalanceAtomic(
                        amount=Decimal("0.5"),
                        amount_atomic=int(0.5 * 10**18),
                        asset=bnb_token,
                        decimals=18,
                    ),
                    buy_balance=BalanceAtomic(
                        amount=Decimal("0.5"),
                        amount_atomic=int(0.5 * 10**18),
                        asset=wbnb_token,
                        decimals=18,
                    ),
                    type="BUY",
                    asset_type="TOKEN",
                    tries=[],
                    created_at=1752268296,
                    status="PENDING",
                    trigger="MANUAL",
                    buy_basket_id=None,
                ),
            ],
            [
                Order(
                    id="2",
                    sell_balance=BalanceAtomic(
                        amount=Decimal("0.5"),
                        amount_atomic=int(0.5 * 10**18),
                        asset=bnb_token,
                        decimals=18,
                    ),
                    buy_balance=BalanceAtomic(
                        amount=Decimal("0.08"),
                        amount_atomic=int(0.08 * 10**18),
                        asset=eth_token,
                        decimals=18,
                    ),
                    type="BUY",
                    asset_type="TOKEN",
                    tries=[],
                    created_at=1752268296,
                    status="PENDING",
                    trigger="MANUAL",
                    buy_basket_id=None,
                ),
            ],
        ]
    )


@mark.asyncio
async def test_execute_investment_plan_use_case_buy_only_baskets(
    id_generator: IdGenerator,
    date_time: DateTime,
    order_submitter: OrderSubmitter,
    exchange: Exchange,
    chain: Chain,
    posting_repository: PostingRepository,
    investment_parameters: InvestmentParameters,
    use_case: ExecuteInvestmentPlanUseCase,
):
    date_time.now.return_value = 1752268296
    id_generator.generate_random_id.side_effect = ["100", "1", "2", "101", "3", "4"]
    posting_repository.get_holding_balances.return_value = []
    chain.get_native_token_balance.return_value = BalanceAtomic(
        amount=Decimal("75"),
        amount_atomic=75 * 10**18,
        decimals=18,
        asset=bnb_token,
    )

    exchange.convert_balance_to_token.side_effect = [
        ExchangeConvertedBalance(
            sell_balance=BalanceAtomic(
                amount=Decimal("0.25"),
                amount_atomic=int(0.25 * 10**18),
                asset=bnb_token,
                decimals=18,
            ),
            buy_balance=BalanceAtomic(
                amount=Decimal("0.25"),
                amount_atomic=int(0.25 * 10**18),
                asset=wbnb_token,
                decimals=18,
            ),
        ),
        ExchangeConvertedBalance(
            sell_balance=BalanceAtomic(
                amount=Decimal("0.25"),
                amount_atomic=int(0.25 * 10**18),
                asset=bnb_token,
                decimals=18,
            ),
            buy_balance=BalanceAtomic(
                amount=Decimal("0.10"),
                amount_atomic=int(0.10 * 10**18),
                asset=eth_token,
                decimals=18,
            ),
        ),
        ExchangeConvertedBalance(
            sell_balance=BalanceAtomic(
                amount=Decimal("0.40"),
                amount_atomic=int(0.40 * 10**18),
                asset=bnb_token,
                decimals=18,
            ),
            buy_balance=BalanceAtomic(
                amount=Decimal("0.30"),
                amount_atomic=int(0.30 * 10**18),
                asset=sol_token,
                decimals=18,
            ),
        ),
        ExchangeConvertedBalance(
            sell_balance=BalanceAtomic(
                amount=Decimal("0.40"),
                amount_atomic=int(0.40 * 10**18),
                asset=bnb_token,
                decimals=18,
            ),
            buy_balance=BalanceAtomic(
                amount=Decimal("60"),
                amount_atomic=int(60 * 10**18),
                asset=usdt_token,
                decimals=18,
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
                    decimals=18,
                ),
                token=wbnb_token,
                investment_parameters=investment_parameters,
            ),
            mock.call.convert_balance_to_token(
                balance=BalanceAtomic(
                    amount=Decimal("0.25"),
                    amount_atomic=int(0.25 * 10**18),
                    asset=bnb_token,
                    decimals=18,
                ),
                token=eth_token,
                investment_parameters=investment_parameters,
            ),
            mock.call.convert_balance_to_token(
                balance=BalanceAtomic(
                    amount=Decimal("0.40"),
                    amount_atomic=int(0.40 * 10**18),
                    asset=bnb_token,
                    decimals=18,
                ),
                token=sol_token,
                investment_parameters=investment_parameters,
            ),
            mock.call.convert_balance_to_token(
                balance=BalanceAtomic(
                    amount=Decimal("0.40"),
                    amount_atomic=int(0.40 * 10**18),
                    asset=bnb_token,
                    decimals=18,
                ),
                token=usdt_token,
                investment_parameters=investment_parameters,
            ),
        ]
    )

    order_submitter.submit_orders.assert_called_once_with(
        [
            [
                Order(
                    id="100",
                    sell_balance=BalanceAtomic(
                        amount=Decimal("0.5"),
                        amount_atomic=int(0.5 * 10**18),
                        asset=bnb_token,
                        decimals=18,
                    ),
                    buy_balance=BalanceAtomic(
                        amount=Decimal("1"),
                        amount_atomic=int(1 * 10**18),
                        asset=Basket(
                            id="basket1",
                            name="Basket 1",
                            display_name="Basket 1",
                            ticker="BASK1",
                            description="A sample basket",
                            denomination=Decimal(1),
                            tokens=[wbnb_token, eth_token],
                        ),
                        decimals=18,
                    ),
                    type="BUY",
                    asset_type="BASKET",
                    tries=[],
                    created_at=1752268296,
                    status="PENDING",
                    trigger="MANUAL",
                    buy_basket_id="basket1",
                ),
                Order(
                    id="1",
                    parent_order_id="100",
                    sell_balance=BalanceAtomic(
                        amount=Decimal("0.25"),
                        amount_atomic=int(0.25 * 10**18),
                        asset=bnb_token,
                        decimals=18,
                    ),
                    buy_balance=BalanceAtomic(
                        amount=Decimal("0.25"),
                        amount_atomic=int(0.25 * 10**18),
                        asset=wbnb_token,
                        decimals=18,
                    ),
                    type="BUY",
                    asset_type="TOKEN",
                    tries=[],
                    created_at=1752268296,
                    status="PENDING",
                    trigger="MANUAL",
                    buy_basket_id="basket1",
                ),
                Order(
                    id="2",
                    parent_order_id="100",
                    sell_balance=BalanceAtomic(
                        amount=Decimal("0.25"),
                        amount_atomic=int(0.25 * 10**18),
                        asset=bnb_token,
                        decimals=18,
                    ),
                    buy_balance=BalanceAtomic(
                        amount=Decimal("0.10"),
                        amount_atomic=int(0.10 * 10**18),
                        asset=eth_token,
                        decimals=18,
                    ),
                    type="BUY",
                    asset_type="TOKEN",
                    tries=[],
                    created_at=1752268296,
                    status="PENDING",
                    trigger="MANUAL",
                    buy_basket_id="basket1",
                ),
            ],
            [
                Order(
                    id="101",
                    sell_balance=BalanceAtomic(
                        amount=Decimal("0.80"),
                        amount_atomic=int(0.80 * 10**18),
                        asset=bnb_token,
                        decimals=18,
                    ),
                    buy_balance=BalanceAtomic(
                        amount=Decimal("1"),
                        amount_atomic=int(1 * 10**18),
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
                        decimals=18,
                    ),
                    type="BUY",
                    asset_type="BASKET",
                    tries=[],
                    created_at=1752268296,
                    status="PENDING",
                    trigger="MANUAL",
                    buy_basket_id="basket2",
                ),
                Order(
                    id="3",
                    parent_order_id="101",
                    sell_balance=BalanceAtomic(
                        amount=Decimal("0.40"),
                        amount_atomic=int(0.40 * 10**18),
                        asset=bnb_token,
                        decimals=18,
                    ),
                    buy_balance=BalanceAtomic(
                        amount=Decimal("0.30"),
                        amount_atomic=int(0.30 * 10**18),
                        asset=sol_token,
                        decimals=18,
                    ),
                    type="BUY",
                    asset_type="TOKEN",
                    tries=[],
                    created_at=1752268296,
                    status="PENDING",
                    trigger="MANUAL",
                    buy_basket_id="basket2",
                ),
                Order(
                    id="4",
                    parent_order_id="101",
                    sell_balance=BalanceAtomic(
                        amount=Decimal("0.40"),
                        amount_atomic=int(0.40 * 10**18),
                        asset=bnb_token,
                        decimals=18,
                    ),
                    buy_balance=BalanceAtomic(
                        amount=Decimal("60"),
                        amount_atomic=int(60 * 10**18),
                        asset=usdt_token,
                        decimals=18,
                    ),
                    type="BUY",
                    asset_type="TOKEN",
                    tries=[],
                    created_at=1752268296,
                    status="PENDING",
                    trigger="MANUAL",
                    buy_basket_id="basket2",
                ),
            ],
        ]
    )


@mark.asyncio
async def test_execute_investment_plan_use_case_buy_token_and_basket(
    id_generator: IdGenerator,
    date_time: DateTime,
    order_submitter: OrderSubmitter,
    exchange: Exchange,
    chain: Chain,
    posting_repository: PostingRepository,
    use_case: ExecuteInvestmentPlanUseCase,
):
    date_time.now.return_value = 1752268296
    id_generator.generate_random_id.side_effect = ["100", "1", "2", "3", "4"]
    posting_repository.get_holding_balances.return_value = []
    chain.get_native_token_balance.return_value = BalanceAtomic(
        amount=Decimal("75"),
        amount_atomic=75 * 10**18,
        decimals=18,
        asset=bnb_token,
    )

    exchange.convert_balance_to_token.side_effect = [
        ExchangeConvertedBalance(
            sell_balance=BalanceAtomic(
                amount=Decimal("0.25"),
                amount_atomic=int(0.25 * 10**18),
                asset=bnb_token,
                decimals=18,
            ),
            buy_balance=BalanceAtomic(
                amount=Decimal("0.25"),
                amount_atomic=int(0.25 * 10**18),
                asset=wbnb_token,
                decimals=18,
            ),
        ),
        ExchangeConvertedBalance(
            sell_balance=BalanceAtomic(
                amount=Decimal("0.25"),
                amount_atomic=int(0.25 * 10**18),
                asset=bnb_token,
                decimals=18,
            ),
            buy_balance=BalanceAtomic(
                amount=Decimal("0.08"),
                amount_atomic=int(0.08 * 10**18),
                asset=eth_token,
                decimals=18,
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
            [
                Order(
                    id="100",
                    sell_balance=BalanceAtomic(
                        amount=Decimal("0.5"),
                        amount_atomic=int(0.5 * 10**18),
                        asset=bnb_token,
                        decimals=18,
                    ),
                    buy_balance=BalanceAtomic(
                        amount=Decimal("1"),
                        amount_atomic=int(1 * 10**18),
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
                        decimals=18,
                    ),
                    type="BUY",
                    asset_type="BASKET",
                    tries=[],
                    created_at=1752268296,
                    status="PENDING",
                    trigger="MANUAL",
                    buy_basket_id="basket1",
                ),
                Order(
                    id="1",
                    parent_order_id="100",
                    sell_balance=BalanceAtomic(
                        amount=Decimal("0.25"),
                        amount_atomic=int(0.25 * 10**18),
                        asset=bnb_token,
                        decimals=18,
                    ),
                    buy_balance=BalanceAtomic(
                        amount=Decimal("0.25"),
                        amount_atomic=int(0.25 * 10**18),
                        asset=wbnb_token,
                        decimals=18,
                    ),
                    type="BUY",
                    asset_type="TOKEN",
                    tries=[],
                    created_at=1752268296,
                    status="PENDING",
                    trigger="MANUAL",
                    buy_basket_id="basket1",
                ),
                Order(
                    id="2",
                    parent_order_id="100",
                    sell_balance=BalanceAtomic(
                        amount=Decimal("0.25"),
                        amount_atomic=int(0.25 * 10**18),
                        asset=bnb_token,
                        decimals=18,
                    ),
                    buy_balance=BalanceAtomic(
                        amount=Decimal("0.08"),
                        amount_atomic=int(0.08 * 10**18),
                        asset=eth_token,
                        decimals=18,
                    ),
                    type="BUY",
                    asset_type="TOKEN",
                    tries=[],
                    created_at=1752268296,
                    status="PENDING",
                    trigger="MANUAL",
                    buy_basket_id="basket1",
                ),
            ],
            [
                Order(
                    id="3",
                    sell_balance=BalanceAtomic(
                        amount=Decimal("0.50"),
                        amount_atomic=int(0.50 * 10**18),
                        asset=bnb_token,
                        decimals=18,
                    ),
                    buy_balance=BalanceAtomic(
                        amount=Decimal("0.50"),
                        amount_atomic=int(0.50 * 10**18),
                        asset=wbnb_token,
                        decimals=18,
                    ),
                    type="BUY",
                    asset_type="TOKEN",
                    tries=[],
                    created_at=1752268296,
                    status="PENDING",
                    trigger="MANUAL",
                    buy_basket_id=None,
                )
            ],
        ]
    )


@mark.asyncio
async def test_execute_investment_plan_use_case_buy_basket_sell_basket(
    id_generator: IdGenerator,
    date_time: DateTime,
    chain: Chain,
    posting_repository: PostingRepository,
    use_case: ExecuteInvestmentPlanUseCase,
):
    date_time.now.return_value = 1752268296
    id_generator.generate_random_id.side_effect = ["1", "2", "3", "4"]
    posting_repository.get_holding_balances.return_value = []
    chain.get_native_token_balance.return_value = BalanceAtomic(
        amount=Decimal("75"),
        amount_atomic=75 * 10**18,
        decimals=18,
        asset=bnb_token,
    )

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
    posting_repository: PostingRepository,
    chain: Chain,
    use_case: ExecuteInvestmentPlanUseCase,
):
    date_time.now.return_value = 1752268296
    id_generator.generate_random_id.side_effect = ["1", "2"]
    posting_repository.get_holding_balances.return_value = [
        Holding(
            balance=BalanceAtomic(
                amount=Decimal("75"),
                amount_atomic=75 * 10**18,
                decimals=18,
                asset=wbnb_token,
            ),
            children=None,
        ),
        Holding(
            balance=BalanceAtomic(
                amount=Decimal("75"),
                amount_atomic=75 * 10**18,
                decimals=18,
                asset=eth_token,
            ),
            children=None,
        ),
    ]
    chain.get_native_token_balance.return_value = BalanceAtomic(
        amount=Decimal("75"),
        amount_atomic=75 * 10**18,
        decimals=18,
        asset=bnb_token,
    )

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
            [
                Order(
                    id="1",
                    sell_balance=BalanceAtomic(
                        amount=Decimal("0.5"),
                        amount_atomic=int(0.5 * 10**18),
                        asset=wbnb_token,
                        decimals=18,
                    ),
                    buy_balance=BalanceAtomic(
                        amount=Decimal("0.5"),
                        amount_atomic=int(0.5 * 10**18),
                        asset=bnb_token,
                        decimals=18,
                    ),
                    type="SELL",
                    asset_type="TOKEN",
                    tries=[],
                    created_at=1752268296,
                    status="PENDING",
                    trigger="MANUAL",
                    buy_basket_id=None,
                ),
            ],
            [
                Order(
                    id="2",
                    sell_balance=BalanceAtomic(
                        amount=Decimal("0.08"),
                        amount_atomic=int(0.08 * 10**18),
                        asset=eth_token,
                        decimals=18,
                    ),
                    buy_balance=BalanceAtomic(
                        amount=Decimal("0.5"),
                        amount_atomic=int(0.5 * 10**18),
                        asset=bnb_token,
                        decimals=18,
                    ),
                    type="SELL",
                    asset_type="TOKEN",
                    tries=[],
                    created_at=1752268296,
                    status="PENDING",
                    trigger="MANUAL",
                    buy_basket_id=None,
                ),
            ],
        ]
    )


@mark.asyncio
async def test_execute_investment_plan_use_case_sell_only_baskets(
    id_generator: IdGenerator,
    date_time: DateTime,
    order_submitter: OrderSubmitter,
    exchange: Exchange,
    posting_repository: PostingRepository,
    chain: Chain,
    investment_parameters: InvestmentParameters,
    use_case: ExecuteInvestmentPlanUseCase,
):
    basket1 = Basket(
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
    )
    basket2 = Basket(
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
    )

    date_time.now.return_value = 1752268296
    id_generator.generate_random_id.side_effect = ["100", "1", "2", "101", "3", "4"]
    posting_repository.get_holding_balances.return_value = [
        Holding(
            balance=BalanceAtomic(
                amount=Decimal("5"),
                amount_atomic=5 * 10**18,
                decimals=18,
                asset=wbnb_token,
            ),
            children=None,
        ),
        Holding(
            balance=BalanceAtomic(
                amount=Decimal("75"),
                amount_atomic=75 * 10**18,
                decimals=18,
                asset=sol_token,
            ),
            children=None,
        ),
        Holding(
            balance=BalanceAtomic(
                amount=Decimal("75"),
                amount_atomic=75 * 10**18,
                decimals=18,
                asset=eth_token,
            ),
            children=None,
        ),
        Holding(
            balance=BalanceAtomic(
                amount=Decimal("75"),
                amount_atomic=75 * 10**18,
                decimals=18,
                asset=usdt_token,
            ),
            children=None,
        ),
        Holding(
            balance=BalanceAtomic(
                amount=Decimal("5"),
                amount_atomic=5 * 10**18,
                decimals=18,
                asset=basket1,
            ),
            children=[
                BalanceAtomic(
                    amount=Decimal("0.25"),
                    amount_atomic=25 * 10**16,
                    decimals=18,
                    asset=wbnb_token,
                ),
                BalanceAtomic(
                    amount=Decimal("0.08"),
                    amount_atomic=8 * 10**16,
                    decimals=18,
                    asset=eth_token,
                ),
            ],
        ),
        Holding(
            balance=BalanceAtomic(
                amount=Decimal("3"),
                amount_atomic=3 * 10**18,
                decimals=18,
                asset=basket2,
            ),
            children=[
                BalanceAtomic(
                    amount=Decimal("0.6"),
                    amount_atomic=6 * 10**17,
                    decimals=18,
                    asset=sol_token,
                ),
                BalanceAtomic(
                    amount=Decimal("0.2"),
                    amount_atomic=2 * 10**17,
                    decimals=18,
                    asset=usdt_token,
                ),
            ],
        ),
    ]
    chain.get_native_token_balance.return_value = BalanceAtomic(
        amount=Decimal("75"),
        amount_atomic=75 * 10**18,
        decimals=18,
        asset=bnb_token,
    )
    exchange.convert_balance_to_token.side_effect = [
        ExchangeConvertedBalance(
            sell_balance=BalanceAtomic(
                amount=Decimal("0.25") / Decimal("5"),
                amount_atomic=int((0.25 / 5) * 10**18),
                asset=wbnb_token,
                decimals=18,
            ),
            buy_balance=BalanceAtomic(
                amount=Decimal("0.25"),
                amount_atomic=int(0.25 * 10**18),
                asset=bnb_token,
                decimals=18,
            ),
        ),
        ExchangeConvertedBalance(
            sell_balance=BalanceAtomic(
                amount=Decimal("0.08") / Decimal("5"),
                amount_atomic=int((0.08 / 5) * 10**18),
                asset=eth_token,
                decimals=18,
            ),
            buy_balance=BalanceAtomic(
                amount=Decimal("0.25"),
                amount_atomic=int(0.25 * 10**18),
                asset=bnb_token,
                decimals=18,
            ),
        ),
        ExchangeConvertedBalance(
            sell_balance=BalanceAtomic(
                amount=Decimal("0.6"),
                amount_atomic=int(0.6 * 10**18),
                asset=sol_token,
                decimals=18,
            ),
            buy_balance=BalanceAtomic(
                amount=Decimal("0.4"),
                amount_atomic=int(0.4 * 10**18),
                asset=bnb_token,
                decimals=18,
            ),
        ),
        ExchangeConvertedBalance(
            sell_balance=BalanceAtomic(
                amount=Decimal("0.2"),
                amount_atomic=int(0.2 * 10**18),
                asset=usdt_token,
                decimals=18,
            ),
            buy_balance=BalanceAtomic(
                amount=Decimal("0.4"),
                amount_atomic=int(0.4 * 10**18),
                asset=bnb_token,
                decimals=18,
            ),
        ),
    ]

    await use_case.execute(
        InvestmentPlan(
            steps=[
                InvestmentPlanStep(
                    buy_balance=Balance(amount=Decimal("1"), asset=bnb_token),
                    sell_balance=Balance(
                        amount=Decimal(1),
                        asset=basket1,
                    ),
                ),
                InvestmentPlanStep(
                    buy_balance=Balance(amount=Decimal("3"), asset=bnb_token),
                    sell_balance=Balance(
                        amount=Decimal(3),
                        asset=basket2,
                    ),
                ),
            ]
        )
    )

    exchange.assert_has_calls(
        [
            mock.call.convert_balance_to_token(
                balance=BalanceAtomic(
                    amount=Decimal("0.25") / Decimal("5"),
                    amount_atomic=int((0.25 / 5) * 10**18),
                    asset=wbnb_token,
                    decimals=18,
                ),
                token=bnb_token,
                investment_parameters=investment_parameters,
            ),
            mock.call.convert_balance_to_token(
                balance=BalanceAtomic(
                    amount=Decimal("0.08") / Decimal("5"),
                    amount_atomic=int((0.08 / 5) * 10**18),
                    asset=eth_token,
                    decimals=18,
                ),
                token=bnb_token,
                investment_parameters=investment_parameters,
            ),
            mock.call.convert_balance_to_token(
                balance=BalanceAtomic(
                    amount=Decimal("0.6"),
                    amount_atomic=int(0.6 * 10**18),
                    asset=sol_token,
                    decimals=18,
                ),
                token=bnb_token,
                investment_parameters=investment_parameters,
            ),
            mock.call.convert_balance_to_token(
                balance=BalanceAtomic(
                    amount=Decimal("0.2"),
                    amount_atomic=2 * 10**17,
                    asset=usdt_token,
                    decimals=18,
                ),
                token=bnb_token,
                investment_parameters=investment_parameters,
            ),
        ]
    )

    order_submitter.submit_orders.assert_called_once_with(
        [
            [
                Order(
                    id="100",
                    sell_balance=BalanceAtomic(
                        amount=Decimal("1"),
                        amount_atomic=int(1 * 10**18),
                        asset=basket1,
                        decimals=18,
                    ),
                    buy_balance=BalanceAtomic(
                        amount=Decimal("1"),
                        amount_atomic=int(1 * 10**18),
                        asset=bnb_token,
                        decimals=18,
                    ),
                    type="SELL",
                    asset_type="BASKET",
                    tries=[],
                    created_at=1752268296,
                    status="PENDING",
                    trigger="MANUAL",
                    sell_basket_id="basket1",
                ),
                Order(
                    id="1",
                    parent_order_id="100",
                    sell_balance=BalanceAtomic(
                        amount=Decimal("0.25") / Decimal("5"),
                        amount_atomic=int((0.25 / 5) * 10**18),
                        asset=wbnb_token,
                        decimals=18,
                    ),
                    buy_balance=BalanceAtomic(
                        amount=Decimal("0.25"),
                        amount_atomic=int(0.25 * 10**18),
                        asset=bnb_token,
                        decimals=18,
                    ),
                    type="SELL",
                    asset_type="TOKEN",
                    tries=[],
                    created_at=1752268296,
                    status="PENDING",
                    trigger="MANUAL",
                    sell_basket_id="basket1",
                ),
                Order(
                    id="2",
                    parent_order_id="100",
                    sell_balance=BalanceAtomic(
                        amount=Decimal("0.08") / Decimal("5"),
                        amount_atomic=int((0.08 / 5) * 10**18),
                        asset=eth_token,
                        decimals=18,
                    ),
                    buy_balance=BalanceAtomic(
                        amount=Decimal("0.25"),
                        amount_atomic=int(0.25 * 10**18),
                        asset=bnb_token,
                        decimals=18,
                    ),
                    type="SELL",
                    asset_type="TOKEN",
                    tries=[],
                    created_at=1752268296,
                    status="PENDING",
                    trigger="MANUAL",
                    sell_basket_id="basket1",
                ),
            ],
            [
                Order(
                    id="101",
                    sell_balance=BalanceAtomic(
                        amount=Decimal("3"),
                        amount_atomic=int(3 * 10**18),
                        asset=basket2,
                        decimals=18,
                    ),
                    buy_balance=BalanceAtomic(
                        amount=Decimal("3"),
                        amount_atomic=int(3 * 10**18),
                        asset=bnb_token,
                        decimals=18,
                    ),
                    type="SELL",
                    asset_type="BASKET",
                    tries=[],
                    created_at=1752268296,
                    status="PENDING",
                    trigger="MANUAL",
                    sell_basket_id="basket2",
                ),
                Order(
                    id="3",
                    parent_order_id="101",
                    sell_balance=BalanceAtomic(
                        amount=Decimal("0.6"),
                        amount_atomic=int(0.6 * 10**18),
                        asset=sol_token,
                        decimals=18,
                    ),
                    buy_balance=BalanceAtomic(
                        amount=Decimal("0.4"),
                        amount_atomic=int(0.4 * 10**18),
                        asset=bnb_token,
                        decimals=18,
                    ),
                    type="SELL",
                    asset_type="TOKEN",
                    tries=[],
                    created_at=1752268296,
                    status="PENDING",
                    trigger="MANUAL",
                    sell_basket_id="basket2",
                ),
                Order(
                    id="4",
                    parent_order_id="101",
                    sell_balance=BalanceAtomic(
                        amount=Decimal("0.2"),
                        amount_atomic=int(0.2 * 10**18),
                        asset=usdt_token,
                        decimals=18,
                    ),
                    buy_balance=BalanceAtomic(
                        amount=Decimal("0.4"),
                        amount_atomic=int(0.4 * 10**18),
                        asset=bnb_token,
                        decimals=18,
                    ),
                    type="SELL",
                    asset_type="TOKEN",
                    tries=[],
                    created_at=1752268296,
                    status="PENDING",
                    trigger="MANUAL",
                    sell_basket_id="basket2",
                ),
            ],
        ]
    )


@mark.asyncio
async def test_execute_investment_plan_use_case_sell_token_and_basket(
    id_generator: IdGenerator,
    date_time: DateTime,
    order_submitter: OrderSubmitter,
    exchange: Exchange,
    posting_repository: PostingRepository,
    chain: Chain,
    use_case: ExecuteInvestmentPlanUseCase,
):
    basket1 = Basket(
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
    )

    date_time.now.return_value = 1752268296
    id_generator.generate_random_id.side_effect = ["100", "1", "2", "3", "4"]
    posting_repository.get_holding_balances.return_value = [
        Holding(
            balance=BalanceAtomic(
                amount=Decimal("75"),
                amount_atomic=75 * 10**18,
                decimals=18,
                asset=wbnb_token,
            ),
            children=None,
        ),
        Holding(
            balance=BalanceAtomic(
                amount=Decimal("75"),
                amount_atomic=75 * 10**18,
                decimals=18,
                asset=eth_token,
            ),
            children=None,
        ),
        Holding(
            balance=BalanceAtomic(
                amount=Decimal("3"),
                amount_atomic=3 * 10**18,
                decimals=18,
                asset=basket1,
            ),
            children=[
                BalanceAtomic(
                    amount=Decimal("1"),
                    amount_atomic=int(1 * 10**18),
                    decimals=18,
                    asset=wbnb_token,
                ),
                BalanceAtomic(
                    amount=Decimal("10"),
                    amount_atomic=int(10 * 10**18),
                    decimals=18,
                    asset=eth_token,
                ),
            ],
        ),
    ]
    chain.get_native_token_balance.return_value = BalanceAtomic(
        amount=Decimal("75"),
        amount_atomic=75 * 10**18,
        decimals=18,
        asset=bnb_token,
    )
    exchange.convert_balance_to_token.side_effect = [
        ExchangeConvertedBalance(
            sell_balance=BalanceAtomic(
                amount=Decimal("1"),
                amount_atomic=int(1 * 10**18),
                asset=wbnb_token,
                decimals=18,
            ),
            buy_balance=BalanceAtomic(
                amount=Decimal("0.25"),
                amount_atomic=int(0.25 * 10**18),
                asset=bnb_token,
                decimals=18,
            ),
        ),
        ExchangeConvertedBalance(
            sell_balance=BalanceAtomic(
                amount=Decimal("10"),
                amount_atomic=int(10 * 10**18),
                asset=eth_token,
                decimals=18,
            ),
            buy_balance=BalanceAtomic(
                amount=Decimal("0.25"),
                amount_atomic=int(0.25 * 10**18),
                asset=bnb_token,
                decimals=18,
            ),
        ),
    ]

    await use_case.execute(
        InvestmentPlan(
            steps=[
                InvestmentPlanStep(
                    buy_balance=Balance(amount=Decimal("0.5"), asset=bnb_token),
                    sell_balance=Balance(
                        amount=Decimal(3),
                        asset=basket1,
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
            [
                Order(
                    id="100",
                    sell_balance=BalanceAtomic(
                        amount=Decimal("3"),
                        amount_atomic=int(3 * 10**18),
                        asset=basket1,
                        decimals=18,
                    ),
                    buy_balance=BalanceAtomic(
                        amount=Decimal("0.5"),
                        amount_atomic=int(0.5 * 10**18),
                        asset=bnb_token,
                        decimals=18,
                    ),
                    type="SELL",
                    asset_type="BASKET",
                    tries=[],
                    created_at=1752268296,
                    status="PENDING",
                    trigger="MANUAL",
                    sell_basket_id="basket1",
                ),
                Order(
                    id="1",
                    parent_order_id="100",
                    sell_balance=BalanceAtomic(
                        amount=Decimal("1"),
                        amount_atomic=int(1 * 10**18),
                        asset=wbnb_token,
                        decimals=18,
                    ),
                    buy_balance=BalanceAtomic(
                        amount=Decimal("0.25"),
                        amount_atomic=int(0.25 * 10**18),
                        asset=bnb_token,
                        decimals=18,
                    ),
                    type="SELL",
                    asset_type="TOKEN",
                    tries=[],
                    created_at=1752268296,
                    status="PENDING",
                    trigger="MANUAL",
                    sell_basket_id="basket1",
                ),
                Order(
                    id="2",
                    parent_order_id="100",
                    sell_balance=BalanceAtomic(
                        amount=Decimal("10"),
                        amount_atomic=int(10 * 10**18),
                        asset=eth_token,
                        decimals=18,
                    ),
                    buy_balance=BalanceAtomic(
                        amount=Decimal("0.25"),
                        amount_atomic=int(0.25 * 10**18),
                        asset=bnb_token,
                        decimals=18,
                    ),
                    type="SELL",
                    asset_type="TOKEN",
                    tries=[],
                    created_at=1752268296,
                    status="PENDING",
                    trigger="MANUAL",
                    sell_basket_id="basket1",
                ),
            ],
            [
                Order(
                    id="3",
                    sell_balance=BalanceAtomic(
                        amount=Decimal("0.5"),
                        amount_atomic=int(0.5 * 10**18),
                        asset=wbnb_token,
                        decimals=18,
                    ),
                    buy_balance=BalanceAtomic(
                        amount=Decimal("0.5"),
                        amount_atomic=int(0.5 * 10**18),
                        asset=bnb_token,
                        decimals=18,
                    ),
                    type="SELL",
                    asset_type="TOKEN",
                    tries=[],
                    created_at=1752268296,
                    status="PENDING",
                    trigger="MANUAL",
                    buy_basket_id=None,
                ),
            ],
        ]
    )
