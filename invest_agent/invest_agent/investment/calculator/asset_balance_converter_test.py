from decimal import Decimal
from unittest import mock
from invest_agent.chain.balance import BalanceAtomic
from invest_agent.chain.chain import Chain
from invest_agent.investment.calculator.asset_balance_converter import (
    AssetBalanceConverter,
    ConvertedBalance,
)
from invest_agent.investment.exception.cannot_swap_basket_for_another_exception import (
    CannotSwapBasketForAnotherException,
)
from invest_agent.investment.exchange.exchange import Exchange, ExchangeConvertedBalance
from invest_agent.portfolio.holding.holding import Holding
from protocol.basket import Basket
from protocol.token import Token
from pytest import fixture, raises, mark

from protocol.fixture.basket import test_basket, big4_basket
from protocol.fixture.token import btc_token, eth_token, sol_token


@fixture
def chain():
    chain = mock.Mock(spec=Chain)
    chain.get_token_decimals.return_value = 10

    return chain


@fixture
def exchange():
    exchange = mock.Mock(spec=Exchange)

    exchange.convert_balance_to_token.side_effect = (
        lambda balance, token, investment_parameters: ExchangeConvertedBalance(
            sell_balance=balance,
            buy_balance=BalanceAtomic(
                asset=token,
                amount=balance.amount * Decimal("10"),
                amount_atomic=balance.amount_atomic * 10,
                decimals=18,
            ),
        )
    )

    return exchange


@fixture
def asset_balance_converter(exchange: Exchange, chain: Chain):
    return AssetBalanceConverter(exchange=exchange, chain=chain)


@mark.asyncio
async def test_asset_balance_converter_sell_basket_to_buy_basket_should_raise(
    asset_balance_converter: AssetBalanceConverter,
):
    sell_balance = BalanceAtomic(
        asset=test_basket, amount=Decimal("0"), amount_atomic=0, decimals=18
    )

    holdings: list[Holding] = []

    with raises(CannotSwapBasketForAnotherException):
        await asset_balance_converter.convert(sell_balance, big4_basket, holdings)


@mark.asyncio
async def test_asset_balance_converter_sell_basket_to_buy_token(
    asset_balance_converter: AssetBalanceConverter,
):
    sell_balance = BalanceAtomic(
        asset=test_basket, amount=Decimal("50"), amount_atomic=50, decimals=18
    )

    holdings: list[Holding] = [
        Holding(
            balance=BalanceAtomic(
                asset=test_basket,
                amount=Decimal("100"),
                amount_atomic=100,
                decimals=18,
            ),
            children=[
                BalanceAtomic(
                    asset=eth_token,
                    amount=Decimal("78"),
                    amount_atomic=78 * 10**18,
                    decimals=18,
                ),
                BalanceAtomic(
                    asset=btc_token,
                    amount=Decimal("24"),
                    amount_atomic=24 * 10**18,
                    decimals=18,
                ),
            ],
        )
    ]

    convert_asset_balance = await asset_balance_converter.convert(
        sell_balance, sol_token, holdings
    )

    assert convert_asset_balance.total_balance == ConvertedBalance(
        sell_balance=BalanceAtomic(
            asset=test_basket, amount=Decimal("50"), amount_atomic=50, decimals=18
        ),
        buy_balance=BalanceAtomic(
            asset=sol_token,
            amount=Decimal("510"),
            amount_atomic=510 * 10**18,
            decimals=18,
        ),
    )

    assert convert_asset_balance.balances == [
        ConvertedBalance(
            sell_balance=BalanceAtomic(
                asset=eth_token,
                amount=Decimal("39"),
                amount_atomic=39 * 10**18,
                decimals=18,
            ),
            buy_balance=BalanceAtomic(
                asset=sol_token,
                amount=Decimal("390"),
                amount_atomic=390 * 10**18,
                decimals=18,
            ),
        ),
        ConvertedBalance(
            sell_balance=BalanceAtomic(
                asset=btc_token,
                amount=Decimal("12"),
                amount_atomic=12 * 10**18,
                decimals=18,
            ),
            buy_balance=BalanceAtomic(
                asset=sol_token,
                amount=Decimal("120"),
                amount_atomic=120 * 10**18,
                decimals=18,
            ),
        ),
    ]


@mark.asyncio
async def test_asset_balance_converter_sell_basket_to_buy_token_no_holdings(
    asset_balance_converter: AssetBalanceConverter,
):
    sell_balance = BalanceAtomic(
        asset=test_basket, amount=Decimal("50"), amount_atomic=50, decimals=18
    )

    holdings: list[Holding] = [
        Holding(
            balance=BalanceAtomic(
                asset=test_basket,
                amount=Decimal("0"),
                amount_atomic=0,
                decimals=18,
            ),
            children=[
                BalanceAtomic(
                    asset=eth_token,
                    amount=Decimal("0"),
                    amount_atomic=0 * 10**18,
                    decimals=18,
                ),
                BalanceAtomic(
                    asset=btc_token,
                    amount=Decimal("0"),
                    amount_atomic=0 * 10**18,
                    decimals=18,
                ),
            ],
        )
    ]

    convert_asset_balance = await asset_balance_converter.convert(
        sell_balance, sol_token, holdings
    )

    assert convert_asset_balance.total_balance == ConvertedBalance(
        sell_balance=BalanceAtomic(
            asset=test_basket, amount=Decimal("50"), amount_atomic=50, decimals=18
        ),
        buy_balance=BalanceAtomic(
            asset=sol_token,
            amount=Decimal("0"),
            amount_atomic=0,
            decimals=10,
        ),
    )

    assert convert_asset_balance.balances == []


@mark.asyncio
async def test_asset_balance_converter_sell_basket_to_buy_token_nil_holding(
    asset_balance_converter: AssetBalanceConverter,
):
    sell_balance = BalanceAtomic(
        asset=test_basket, amount=Decimal("50"), amount_atomic=50, decimals=18
    )

    holdings: list[Holding] = []

    convert_asset_balance = await asset_balance_converter.convert(
        sell_balance, sol_token, holdings
    )

    assert convert_asset_balance.total_balance == ConvertedBalance(
        sell_balance=BalanceAtomic(
            asset=test_basket, amount=Decimal("50"), amount_atomic=50, decimals=18
        ),
        buy_balance=BalanceAtomic(
            asset=sol_token,
            amount=Decimal("0"),
            amount_atomic=0,
            decimals=10,
        ),
    )

    assert convert_asset_balance.balances == []


@mark.asyncio
async def test_asset_balance_converter_buy_basket_to_sell_token(
    asset_balance_converter: AssetBalanceConverter,
):
    sell_balance = BalanceAtomic[Token](
        asset=sol_token, amount=Decimal("88"), amount_atomic=88 * 10**18, decimals=18
    )

    holdings: list[Holding] = [
        Holding(
            balance=BalanceAtomic(
                asset=sol_token,
                amount=Decimal("88"),
                amount_atomic=88 * 10**18,
                decimals=18,
            ),
            children=None,
        )
    ]

    convert_asset_balance = await asset_balance_converter.convert(
        sell_balance, test_basket, holdings
    )

    assert convert_asset_balance.total_balance == ConvertedBalance(
        sell_balance=BalanceAtomic(
            asset=sol_token,
            amount=Decimal("88"),
            amount_atomic=88 * 10**18,
            decimals=18,
        ),
        buy_balance=BalanceAtomic(
            asset=test_basket,
            amount=Decimal("88"),
            amount_atomic=88 * 10**18,
            decimals=18,
        ),
    )
    assert convert_asset_balance.balances == [
        ConvertedBalance(
            sell_balance=BalanceAtomic(
                asset=sol_token,
                amount=Decimal("44"),
                amount_atomic=44 * 10**18,
                decimals=18,
            ),
            buy_balance=BalanceAtomic(
                asset=btc_token,
                amount=Decimal("440"),
                amount_atomic=440 * 10**18,
                decimals=18,
            ),
        ),
        ConvertedBalance(
            sell_balance=BalanceAtomic(
                asset=sol_token,
                amount=Decimal("44"),
                amount_atomic=44 * 10**18,
                decimals=18,
            ),
            buy_balance=BalanceAtomic(
                asset=eth_token,
                amount=Decimal("440"),
                amount_atomic=440 * 10**18,
                decimals=18,
            ),
        ),
    ]


@mark.asyncio
async def test_asset_balance_converter_buy_basket_to_sell_token_basket_without_tokens(
    asset_balance_converter: AssetBalanceConverter,
):
    basket_without_token = Basket(
        id="0d83917d-a2bd-4482-83e6-68d52c8f293a",
        name="Test Basket",
        display_name="Test Basket",
        ticker="TEST",
        description="A basket for testing purposes",
        denomination=Decimal("10.0"),
        tokens=[],
    )

    sell_balance = BalanceAtomic[Token](
        asset=sol_token, amount=Decimal("88"), amount_atomic=88 * 10**18, decimals=18
    )

    holdings: list[Holding] = []

    convert_asset_balance = await asset_balance_converter.convert(
        sell_balance, basket_without_token, holdings
    )

    assert convert_asset_balance.total_balance == ConvertedBalance(
        sell_balance=BalanceAtomic(
            asset=sol_token,
            amount=Decimal("88"),
            amount_atomic=88 * 10**18,
            decimals=18,
        ),
        buy_balance=BalanceAtomic(
            asset=basket_without_token,
            amount=Decimal("0"),
            amount_atomic=0,
            decimals=10,
        ),
    )
    assert convert_asset_balance.balances == []


@mark.asyncio
async def test_asset_balance_converter_sell_token_to_buy_token(
    asset_balance_converter: AssetBalanceConverter,
):
    sell_balance = BalanceAtomic[Token](
        asset=sol_token, amount=Decimal("88"), amount_atomic=88 * 10**18, decimals=18
    )

    holdings: list[Holding] = [
        Holding(
            balance=BalanceAtomic(
                asset=sol_token,
                amount=Decimal("88"),
                amount_atomic=88 * 10**18,
                decimals=18,
            ),
            children=None,
        )
    ]

    convert_asset_balance = await asset_balance_converter.convert(
        sell_balance, btc_token, holdings
    )

    assert convert_asset_balance.total_balance == ConvertedBalance(
        sell_balance=BalanceAtomic(
            asset=sol_token,
            amount=Decimal("88"),
            amount_atomic=88 * 10**18,
            decimals=18,
        ),
        buy_balance=BalanceAtomic(
            asset=btc_token,
            amount=Decimal("880"),
            amount_atomic=880 * 10**18,
            decimals=18,
        ),
    )
    assert convert_asset_balance.balances == []
