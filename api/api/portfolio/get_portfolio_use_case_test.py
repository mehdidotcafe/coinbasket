from decimal import Decimal
from unittest import mock
from api.chain.balance import BalanceAtomic
from api.chain.chain import Chain
from api.investment.calculator.asset_balance_converter import (
    AssetBalanceConverter,
    ConvertedAssetBalance,
    ConvertedBalance,
)
from api.investment.exchange.exchange import ExchangeConvertedBalance, Exchange
from api.investment.investment_parameters import InvestmentParameters
from api.portfolio.holding.holding import Holding
from api.portfolio.holding.holding_repository import (
    HoldingRepository,
)
from api.portfolio.get_portfolio_use_case import (
    GetPortfolioUseCase,
    PortfolioBalance,
)
from api.portfolio.small_balance.small_balance_policy import SmallBalancePolicy
from api.address.address import Address
from pytest import fixture, mark

from api.protocol.fixture.token import (
    bnb_token,
    eth_token,
    sol_token,
    wbnb_token,
    usdt_token,
    btc_token,
)
from api.protocol.fixture.basket import big4_basket


@fixture
def holding_repository():
    return mock.Mock(spec=HoldingRepository)


@fixture
def exchange():
    return mock.Mock(spec=Exchange)


@fixture
def chain():
    return mock.Mock(spec=Chain)


@fixture
def asset_balance_converter():
    return mock.Mock(spec=AssetBalanceConverter)


@fixture
def small_balance_policy():
    return mock.Mock(spec=SmallBalancePolicy)


@fixture
def investment_parameters():
    return InvestmentParameters(
        slippage_tolerance_in_percentage=Decimal("1"),
    )


@fixture
def address():
    return Address("0x1234567890abcdef1234567890abcdef12345678")


@fixture
def use_case(
    holding_repository: HoldingRepository,
    exchange: Exchange,
    chain: Chain,
    asset_balance_converter: AssetBalanceConverter,
    small_balance_policy: SmallBalancePolicy,
):
    return GetPortfolioUseCase(
        holding_repository,
        exchange,
        chain,
        asset_balance_converter,
        small_balance_policy,
    )


@mark.asyncio
async def test_get_portfolio_use_case_only_available_balance(
    use_case: GetPortfolioUseCase,
    chain: Chain,
    exchange: Exchange,
    investment_parameters: InvestmentParameters,
    address: Address,
):
    chain.get_native_token_balance.return_value = BalanceAtomic(
        asset=bnb_token,
        amount=Decimal("1000"),
        amount_atomic=1000 * 10**18,
        decimals=18,
    )

    exchange.convert_balance_to_token.side_effect = [
        ExchangeConvertedBalance(
            sell_balance=BalanceAtomic(
                asset=bnb_token,
                amount=Decimal("1000"),
                amount_atomic=1000 * 10**18,
                decimals=18,
            ),
            buy_balance=BalanceAtomic(
                asset=usdt_token,
                amount=Decimal("800000"),
                amount_atomic=800000 * 10**18,
                decimals=18,
            ),
        ),
    ]

    portfolio = await use_case.execute(address, usdt_token)

    chain.get_native_token_balance.assert_called_once()
    exchange.convert_balance_to_token.assert_called_once_with(
        taker=address,
        balance=BalanceAtomic(
            asset=bnb_token,
            amount=Decimal("1000"),
            amount_atomic=1000 * 10**18,
            decimals=18,
        ),
        token=usdt_token,
        investment_parameters=investment_parameters,
    )

    assert portfolio.available_balance == PortfolioBalance(
        native_balance=BalanceAtomic(
            asset=bnb_token,
            amount=Decimal("1000"),
            amount_atomic=1000 * 10**18,
            decimals=18,
        ),
        converted_balance=BalanceAtomic(
            asset=usdt_token,
            amount=Decimal("800000"),
            amount_atomic=800000 * 10**18,
            decimals=18,
        ),
    )


@mark.asyncio
async def test_get_portfolio_use_case_only_pending_orders(
    use_case: GetPortfolioUseCase, address: Address
):
    portfolio = await use_case.execute(address, usdt_token)

    assert portfolio.pending_orders == []


@mark.asyncio
async def test_get_portfolio_use_case_holding_balances(
    use_case: GetPortfolioUseCase,
    holding_repository: HoldingRepository,
    exchange: Exchange,
    chain: Chain,
    asset_balance_converter: AssetBalanceConverter,
    small_balance_policy: SmallBalancePolicy,
    address: Address,
):
    holding_balances: list[Holding] = [
        Holding(
            balance=BalanceAtomic(
                asset=wbnb_token,
                amount=Decimal("1.0"),
                amount_atomic=1 * 10**18,
                decimals=18,
            ),
            children=None,
        ),
        Holding(
            balance=BalanceAtomic(
                asset=sol_token,
                amount=Decimal("4"),
                amount_atomic=4 * 10**18,
                decimals=18,
            ),
            children=None,
        ),
        Holding(
            balance=BalanceAtomic(
                asset=eth_token,
                amount=Decimal("0.85"),
                amount_atomic=85 * 10**16,
                decimals=18,
            ),
            children=None,
        ),
        Holding(
            balance=BalanceAtomic(
                asset=big4_basket,
                amount=Decimal("1000"),
                amount_atomic=1000 * 10**18,
                decimals=18,
            ),
            children=[
                BalanceAtomic(
                    asset=eth_token,
                    amount=Decimal("0.1"),
                    amount_atomic=1 * 10**17,
                    decimals=18,
                ),
                BalanceAtomic(
                    asset=wbnb_token,
                    amount=Decimal("0.5"),
                    amount_atomic=5 * 10**17,
                    decimals=18,
                ),
                BalanceAtomic(
                    asset=sol_token,
                    amount=Decimal("2"),
                    amount_atomic=2 * 10**18,
                    decimals=18,
                ),
                BalanceAtomic(
                    asset=btc_token,
                    amount=Decimal("1"),
                    amount_atomic=1 * 10**18,
                    decimals=18,
                ),
            ],
        ),
    ]

    chain.get_token_decimals.return_value = 18
    holding_repository.get_holding_balances.return_value = holding_balances

    asset_balance_converter.convert.side_effect = [
        ConvertedAssetBalance(
            total_balance=ConvertedBalance(
                sell_balance=BalanceAtomic(
                    asset=wbnb_token,
                    amount=Decimal("1.0"),
                    amount_atomic=1 * 10**18,
                    decimals=18,
                ),
                buy_balance=BalanceAtomic(
                    asset=usdt_token,
                    amount=Decimal("800.0"),
                    amount_atomic=800 * 10**18,
                    decimals=18,
                ),
            ),
            balances=[],
        ),
        ConvertedAssetBalance(
            total_balance=ConvertedBalance(
                sell_balance=BalanceAtomic(
                    asset=sol_token,
                    amount=Decimal("4"),
                    amount_atomic=4 * 10**18,
                    decimals=18,
                ),
                buy_balance=BalanceAtomic(
                    asset=usdt_token,
                    amount=Decimal("600.0"),
                    amount_atomic=600 * 10**18,
                    decimals=18,
                ),
            ),
            balances=[],
        ),
        ConvertedAssetBalance(
            total_balance=ConvertedBalance(
                sell_balance=BalanceAtomic(
                    asset=eth_token,
                    amount=Decimal("0.85"),
                    amount_atomic=85 * 10**16,
                    decimals=18,
                ),
                buy_balance=BalanceAtomic(
                    asset=usdt_token,
                    amount=Decimal("0.001"),
                    amount_atomic=1 * 10**15,
                    decimals=18,
                ),
            ),
            balances=[],
        ),
        ConvertedAssetBalance(
            total_balance=ConvertedBalance(
                sell_balance=BalanceAtomic(
                    asset=big4_basket,
                    amount=Decimal("1000"),
                    amount_atomic=1000 * 10**18,
                    decimals=18,
                ),
                buy_balance=BalanceAtomic(
                    asset=usdt_token,
                    amount=Decimal("36"),
                    amount_atomic=36 * 10**18,
                    decimals=18,
                ),
            ),
            balances=[],
        ),
    ]

    exchange.convert_balance_to_token.side_effect = [
        # Get available_balance mock
        ExchangeConvertedBalance(
            sell_balance=BalanceAtomic(
                asset=bnb_token, amount=Decimal("0"), amount_atomic=0, decimals=18
            ),
            buy_balance=BalanceAtomic(
                asset=usdt_token, amount=Decimal("0"), amount_atomic=0, decimals=18
            ),
        ),
    ]
    small_balance_policy.is_small_balance.side_effect = [False, False, True, False]

    portfolio = await use_case.execute(address, usdt_token)

    holding_repository.get_holding_balances.assert_called_once()
    asset_balance_converter.assert_has_calls(
        [
            mock.call.convert(
                taker=address,
                sell_balance=BalanceAtomic(
                    asset=wbnb_token,
                    amount=Decimal("1.0"),
                    amount_atomic=1 * 10**18,
                    decimals=18,
                ),
                buy_asset=usdt_token,
                holdings=holding_balances,
            ),
            mock.call.convert(
                taker=address,
                sell_balance=BalanceAtomic(
                    asset=sol_token,
                    amount=Decimal("4"),
                    amount_atomic=4 * 10**18,
                    decimals=18,
                ),
                buy_asset=usdt_token,
                holdings=holding_balances,
            ),
            mock.call.convert(
                taker=address,
                sell_balance=BalanceAtomic(
                    asset=eth_token,
                    amount=Decimal("0.85"),
                    amount_atomic=85 * 10**16,
                    decimals=18,
                ),
                buy_asset=usdt_token,
                holdings=holding_balances,
            ),
            mock.call.convert(
                taker=address,
                sell_balance=BalanceAtomic(
                    asset=big4_basket,
                    amount=Decimal("1000"),
                    amount_atomic=1000 * 10**18,
                    decimals=18,
                ),
                buy_asset=usdt_token,
                holdings=holding_balances,
            ),
        ]
    )

    assert portfolio.holding_balances == [
        PortfolioBalance(
            native_balance=BalanceAtomic(
                asset=wbnb_token,
                amount=Decimal("1.0"),
                amount_atomic=1 * 10**18,
                decimals=18,
            ),
            converted_balance=BalanceAtomic(
                asset=usdt_token,
                amount=Decimal("800.0"),
                amount_atomic=800 * 10**18,
                decimals=18,
            ),
        ),
        PortfolioBalance(
            native_balance=BalanceAtomic(
                asset=sol_token,
                amount=Decimal("4"),
                amount_atomic=4 * 10**18,
                decimals=18,
            ),
            converted_balance=BalanceAtomic(
                asset=usdt_token,
                amount=Decimal("600.0"),
                amount_atomic=600 * 10**18,
                decimals=18,
            ),
        ),
        # ETH should be excluded as small balance
        PortfolioBalance(
            native_balance=BalanceAtomic(
                asset=big4_basket,
                amount=Decimal("1000"),
                amount_atomic=1000 * 10**18,
                decimals=18,
            ),
            converted_balance=BalanceAtomic(
                asset=usdt_token,
                amount=Decimal("36"),
                amount_atomic=36 * 10**18,
                decimals=18,
            ),
        ),
    ]


@mark.asyncio
async def test_get_portfolio_use_case_holding_balances_conversion_token_not_usd(
    use_case: GetPortfolioUseCase,
    holding_repository: HoldingRepository,
    exchange: Exchange,
    chain: Chain,
    asset_balance_converter: AssetBalanceConverter,
    small_balance_policy: SmallBalancePolicy,
    address: Address,
):
    holding_balances: list[Holding] = [
        Holding(
            balance=BalanceAtomic(
                asset=wbnb_token,
                amount=Decimal("5.0"),
                amount_atomic=5 * 10**18,
                decimals=18,
            ),
            children=None,
        ),
    ]

    chain.get_token_decimals.return_value = 18
    holding_repository.get_holding_balances.return_value = holding_balances

    asset_balance_converter.convert.side_effect = [
        ConvertedAssetBalance(
            total_balance=ConvertedBalance(
                sell_balance=BalanceAtomic(
                    asset=eth_token,
                    amount=Decimal("1.0"),
                    amount_atomic=1 * 10**18,
                    decimals=18,
                ),
                buy_balance=BalanceAtomic(
                    asset=usdt_token,
                    amount=Decimal("0.001"),
                    amount_atomic=1 * 10**15,
                    decimals=18,
                ),
            ),
            balances=[],
        ),
        ConvertedAssetBalance(
            total_balance=ConvertedBalance(
                sell_balance=BalanceAtomic(
                    asset=wbnb_token,
                    amount=Decimal("5.0"),
                    amount_atomic=5 * 10**18,
                    decimals=18,
                ),
                buy_balance=BalanceAtomic(
                    asset=eth_token,
                    amount=Decimal("9"),
                    amount_atomic=9 * 10**18,
                    decimals=18,
                ),
            ),
            balances=[],
        ),
    ]

    exchange.convert_balance_to_token.side_effect = [
        # Get available_balance mock
        ExchangeConvertedBalance(
            sell_balance=BalanceAtomic(
                asset=bnb_token, amount=Decimal("0"), amount_atomic=0, decimals=18
            ),
            buy_balance=BalanceAtomic(
                asset=usdt_token, amount=Decimal("0"), amount_atomic=0, decimals=18
            ),
        ),
    ]
    small_balance_policy.is_small_balance.return_value = True

    await use_case.execute(address, eth_token)

    small_balance_policy.is_small_balance.assert_called_once_with(
        BalanceAtomic(
            asset=eth_token,
            amount=Decimal("9"),
            amount_atomic=9 * 10**18,
            decimals=18,
        ),
        BalanceAtomic(
            asset=usdt_token,
            amount=Decimal("0.001"),
            amount_atomic=1 * 10**15,
            decimals=18,
        ),
    )


@mark.asyncio
async def test_get_portfolio_use_case_total_balance(
    use_case: GetPortfolioUseCase,
    holding_repository: HoldingRepository,
    exchange: Exchange,
    chain: Chain,
    asset_balance_converter: AssetBalanceConverter,
    small_balance_policy: SmallBalancePolicy,
    address: Address,
):
    holding_balances = [
        Holding(
            balance=BalanceAtomic(
                asset=eth_token,
                amount=Decimal("0.85"),
                amount_atomic=85 * 10**16,
                decimals=18,
            ),
            children=None,
        ),
    ]

    chain.get_native_token_balance.return_value = BalanceAtomic(
        asset=bnb_token,
        amount=Decimal("1000"),
        amount_atomic=1000 * 10**18,
        decimals=18,
    )
    chain.get_token_decimals.return_value = 18
    holding_repository.get_holding_balances.return_value = holding_balances
    asset_balance_converter.convert.side_effect = [
        ConvertedAssetBalance(
            total_balance=ConvertedBalance(
                sell_balance=BalanceAtomic(
                    asset=eth_token,
                    amount=Decimal("0.85"),
                    amount_atomic=85 * 10**16,
                    decimals=18,
                ),
                buy_balance=BalanceAtomic(
                    asset=usdt_token,
                    amount=Decimal("3956"),
                    amount_atomic=3956 * 10**18,
                    decimals=18,
                ),
            ),
            balances=[],
        ),
    ]

    exchange.convert_balance_to_token.side_effect = [
        ExchangeConvertedBalance(
            sell_balance=BalanceAtomic(
                asset=bnb_token,
                amount=Decimal("1000"),
                amount_atomic=1000 * 10**18,
                decimals=18,
            ),
            buy_balance=BalanceAtomic(
                asset=usdt_token,
                amount=Decimal("800000"),
                amount_atomic=800000 * 10**18,
                decimals=18,
            ),
        ),
    ]

    small_balance_policy.is_small_balance.return_value = False

    portfolio = await use_case.execute(address, usdt_token)

    assert portfolio.total_balance == BalanceAtomic(
        asset=usdt_token,
        amount=Decimal("803956"),
        amount_atomic=803956 * 10**18,
        decimals=18,
    )
