from unittest import mock
from api.address.address import Address
from api.chain.balance import BalanceAtomic
from api.chain.chain import Chain
from api.investment.plan_order_use_case import (
    PlanOrderUseCase,
)
from api.investment.calculator.asset_balance_converter import (
    AssetBalanceConverter,
    ConvertedAssetBalance,
    ConvertedBalance,
)
from api.investment.exchange.exchange import Exchange, ExchangeConvertedBalance
from api.investment.intended_order import (
    IntendedOrder,
    IntendedOrderBalance,
)
from api.investment.planned_order import (
    PlannedOrder,
    PlannedOrderBalance,
)
from api.portfolio.holding.holding import Holding
from api.portfolio.holding.holding_repository import HoldingRepository
from pytest import fixture, mark
from api.protocol.fixture.token import eth_token, bnb_token, usdt_token, btc_token
from api.protocol.fixture.basket import big4_basket, test_basket
from decimal import ROUND_DOWN, Decimal


@fixture
def exchange():
    return mock.Mock(spec=Exchange)


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
def holding_repository():
    return mock.Mock(spec=HoldingRepository)


@fixture
def asset_balance_converter():
    return mock.Mock(spec=AssetBalanceConverter)


@fixture
def address():
    return Address("0x1234567890abcdef1234567890abcdef12345678")


@fixture
def use_case(
    exchange: Exchange,
    chain: Chain,
    holding_repository: HoldingRepository,
    asset_balance_converter: AssetBalanceConverter,
):
    return PlanOrderUseCase(
        exchange=exchange,
        chain=chain,
        holding_repository=holding_repository,
        asset_balance_converter=asset_balance_converter,
    )


@mark.asyncio
async def test_plan_order_use_case_execute_defined_sell_token_amount(
    address: Address,
    asset_balance_converter: AssetBalanceConverter,
    holding_repository: HoldingRepository,
    use_case: PlanOrderUseCase,
):
    intended_order = IntendedOrder(
        buy_asset_with_amount=IntendedOrderBalance(
            # amount should be override in PlannedOrder
            asset=eth_token,
            amount=Decimal("1"),
        ),
        sell_asset_with_amount=IntendedOrderBalance(
            asset=bnb_token, amount=Decimal("100")
        ),
    )

    holding_repository.get_holding_balances.return_value = []

    asset_balance_converter.convert.return_value = ConvertedAssetBalance(
        total_balance=ConvertedBalance(
            sell_balance=BalanceAtomic(
                asset=bnb_token,
                amount=Decimal("100"),
                amount_atomic=100 * 10**18,
                decimals=18,
            ),
            buy_balance=BalanceAtomic(
                asset=eth_token,
                amount=Decimal("42"),
                amount_atomic=42 * 10**18,
                decimals=18,
            ),
        ),
        balances=[],
    )

    planned_order = await use_case.execute(address, intended_order)

    assert planned_order == PlannedOrder(
        buy_asset_with_amount=PlannedOrderBalance(
            asset=eth_token, amount=Decimal("42"), available_amount=Decimal("0")
        ),
        sell_asset_with_amount=PlannedOrderBalance(
            asset=bnb_token,
            amount=Decimal("100"),
            available_amount=Decimal("0"),
        ),
    )


@mark.asyncio
async def test_plan_order_use_case_execute_defined_buy_token_amount(
    address: Address,
    exchange: Exchange,
    holding_repository: HoldingRepository,
    use_case: PlanOrderUseCase,
):
    intended_order = IntendedOrder(
        buy_asset_with_amount=IntendedOrderBalance(
            asset=eth_token,
            amount=Decimal("1"),
        ),
        sell_asset_with_amount=IntendedOrderBalance(
            # amount should be override in PlannedOrder
            asset=bnb_token,
            amount=None,
        ),
    )

    holding_repository.get_holding_balances.return_value = []
    exchange.convert_balance_to_token.return_value = ExchangeConvertedBalance(
        buy_balance=BalanceAtomic(
            asset=eth_token,
            amount=Decimal("1"),
            amount_atomic=1 * 10**18,
            decimals=18,
        ),
        sell_balance=BalanceAtomic(
            asset=bnb_token,
            amount=Decimal("100"),
            amount_atomic=100 * 10**18,
            decimals=18,
        ),
    )

    planned_order = await use_case.execute(address, intended_order)

    assert planned_order == PlannedOrder(
        buy_asset_with_amount=PlannedOrderBalance(
            asset=eth_token, amount=Decimal("1"), available_amount=Decimal("0")
        ),
        sell_asset_with_amount=PlannedOrderBalance(
            asset=bnb_token,
            amount=Decimal("100"),
            available_amount=Decimal("0"),
        ),
    )


@mark.asyncio
async def test_plan_order_use_case_execute_same_sell_and_buy_asset(
    address: Address,
    holding_repository: HoldingRepository,
    use_case: PlanOrderUseCase,
):
    intended_order = IntendedOrder(
        buy_asset_with_amount=IntendedOrderBalance(
            asset=eth_token,
            amount=Decimal("1"),
        ),
        sell_asset_with_amount=IntendedOrderBalance(
            asset=eth_token,
            amount=Decimal("1"),
        ),
    )

    holding_repository.get_holding_balances.return_value = []

    planned_order = await use_case.execute(address, intended_order)

    assert planned_order is None


@mark.asyncio
async def test_plan_order_use_case_execute_not_defined_tokens(
    address: Address,
    exchange: Exchange,
    chain: Chain,
    holding_repository: HoldingRepository,
    use_case: PlanOrderUseCase,
):
    intended_order = IntendedOrder(
        buy_asset_with_amount=None,
        sell_asset_with_amount=None,
    )

    holding_repository.get_holding_balances.return_value = []
    chain.get_base_token.return_value = bnb_token

    planned_order = await use_case.execute(address, intended_order)

    assert planned_order is None

    exchange.convert_balance_to_token.assert_not_called()


@mark.asyncio
async def test_plan_order_use_case_execute_not_defined_sell_token(
    address: Address,
    exchange: Exchange,
    chain: Chain,
    holding_repository: HoldingRepository,
    use_case: PlanOrderUseCase,
):
    intended_order = IntendedOrder(
        buy_asset_with_amount=IntendedOrderBalance(
            asset=eth_token,
            amount=None,
        ),
        sell_asset_with_amount=None,
    )

    holding_repository.get_holding_balances.return_value = []
    chain.get_base_token.return_value = bnb_token

    planned_order = await use_case.execute(address, intended_order)

    assert planned_order == PlannedOrder(
        buy_asset_with_amount=PlannedOrderBalance(
            asset=eth_token, amount=None, available_amount=Decimal("0")
        ),
        sell_asset_with_amount=PlannedOrderBalance(
            asset=bnb_token,
            amount=None,
            available_amount=Decimal("0"),
        ),
    )

    exchange.convert_balance_to_token.assert_not_called()


@mark.asyncio
async def test_plan_order_use_case_execute_not_defined_buy_token(
    address: Address,
    exchange: Exchange,
    chain: Chain,
    holding_repository: HoldingRepository,
    use_case: PlanOrderUseCase,
):
    intended_order = IntendedOrder(
        buy_asset_with_amount=None,
        sell_asset_with_amount=IntendedOrderBalance(
            asset=eth_token,
            amount=None,
        ),
    )

    holding_repository.get_holding_balances.return_value = []
    chain.get_base_token.return_value = bnb_token

    planned_order = await use_case.execute(address, intended_order)

    assert planned_order == PlannedOrder(
        buy_asset_with_amount=PlannedOrderBalance(
            asset=bnb_token, amount=None, available_amount=Decimal("0")
        ),
        sell_asset_with_amount=PlannedOrderBalance(
            asset=eth_token,
            amount=None,
            available_amount=Decimal("0"),
        ),
    )

    exchange.convert_balance_to_token.assert_not_called()


@mark.asyncio
async def test_plan_order_use_case_execute_defined_buy_basket_amount(
    address: Address,
    exchange: Exchange,
    holding_repository: HoldingRepository,
    use_case: PlanOrderUseCase,
):
    intended_order = IntendedOrder(
        buy_asset_with_amount=IntendedOrderBalance(
            asset=big4_basket,
            amount=Decimal("50.0"),
        ),
        sell_asset_with_amount=IntendedOrderBalance(
            asset=bnb_token,
            amount=None,
        ),
    )

    holding_repository.get_holding_balances.return_value = []
    exchange.convert_balance_to_token.return_value = ExchangeConvertedBalance(
        sell_balance=BalanceAtomic(
            asset=usdt_token,
            amount=Decimal("500"),
            amount_atomic=500 * 10**18,
            decimals=18,
        ),
        buy_balance=BalanceAtomic(
            asset=bnb_token,
            amount=Decimal("1"),
            amount_atomic=1 * 10**18,
            decimals=18,
        ),
    )

    try:
        await use_case.execute(address, intended_order)
        assert False, "Expected exception for basket not supported"
    except Exception as e:
        assert str(e) == "Baskets are not supported in investment plans."


@mark.asyncio
async def test_plan_order_use_case_execute_defined_sell_basket_amount(
    address: Address,
    asset_balance_converter: AssetBalanceConverter,
    holding_repository: HoldingRepository,
    use_case: PlanOrderUseCase,
):
    intended_order = IntendedOrder(
        buy_asset_with_amount=IntendedOrderBalance(
            asset=bnb_token,
            amount=None,
        ),
        sell_asset_with_amount=IntendedOrderBalance(
            asset=test_basket,
            amount=Decimal("50.0"),
        ),
    )

    holding_repository.get_holding_balances.return_value = [
        Holding(
            balance=BalanceAtomic(
                asset=test_basket,
                amount=Decimal("100"),
                amount_atomic=100 * 10**18,
                decimals=18,
            ),
            children=[
                BalanceAtomic(
                    asset=btc_token,
                    amount=Decimal("800"),
                    amount_atomic=800 * 10**18,
                    decimals=18,
                ),
                BalanceAtomic(
                    asset=eth_token,
                    amount=Decimal("780"),
                    amount_atomic=780 * 10**18,
                    decimals=18,
                ),
            ],
        ),
    ]

    asset_balance_converter.convert.return_value = ConvertedAssetBalance(
        total_balance=ConvertedBalance(
            sell_balance=BalanceAtomic(
                asset=test_basket,
                amount=Decimal("50.0"),
                amount_atomic=50 * 10**18,
                decimals=18,
            ),
            buy_balance=BalanceAtomic(
                asset=bnb_token,
                amount=Decimal("15800"),
                amount_atomic=8000 * 10**18,
                decimals=18,
            ),
        ),
        balances=[],
    )

    try:
        await use_case.execute(address, intended_order)
        assert False, "Expected exception for basket not supported"
    except Exception as e:
        assert str(e) == "Baskets are not supported in investment plans."


@mark.asyncio
async def test_plan_order_use_case_execute_available_amount_defined(
    address: Address,
    exchange: Exchange,
    holding_repository: HoldingRepository,
    use_case: PlanOrderUseCase,
):
    intended_order = IntendedOrder(
        buy_asset_with_amount=IntendedOrderBalance(
            asset=bnb_token,
            amount=None,
        ),
        sell_asset_with_amount=IntendedOrderBalance(
            asset=usdt_token,
            amount=Decimal("200"),
        ),
    )

    holding_repository.get_holding_balances.return_value = [
        Holding(
            balance=BalanceAtomic(
                asset=usdt_token,
                amount=Decimal("80000"),
                amount_atomic=80000 * 10**18,
                decimals=18,
            ),
            children=None,
        ),
        Holding(
            balance=BalanceAtomic(
                asset=bnb_token,
                amount=Decimal("5000"),
                amount_atomic=5000 * 10**18,
                decimals=18,
            ),
            children=None,
        ),
    ]
    exchange.convert_balance_to_token.return_value = ExchangeConvertedBalance(
        sell_balance=BalanceAtomic(
            asset=usdt_token,
            amount=Decimal("200"),
            amount_atomic=500 * 10**18,
            decimals=18,
        ),
        buy_balance=BalanceAtomic(
            asset=bnb_token,
            amount=Decimal("1"),
            amount_atomic=1 * 10**18,
            decimals=18,
        ),
    )

    planned_order = await use_case.execute(address, intended_order)

    assert planned_order is not None

    assert planned_order.buy_asset_with_amount is not None
    assert planned_order.buy_asset_with_amount.available_amount == Decimal("5000")

    assert planned_order.sell_asset_with_amount is not None
    assert planned_order.sell_asset_with_amount.available_amount == Decimal("80000")

    holding_repository.get_holding_balances.assert_called_once()
