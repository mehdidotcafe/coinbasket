from decimal import Decimal
from unittest import mock
from api.address.address import Address
from api.chain.balance import BalanceAtomic
from api.chain.chain import Chain
from api.investment.calculator.asset_balance_converter import (
    AssetBalanceConverter,
    ConvertedBalance,
)
from api.investment.exchange.exchange import Exchange, ExchangeConvertedBalance
from api.investment.fees import Fees
from api.protocol.token import Token
from pytest import fixture, mark

from api.protocol.fixture.basket import test_basket
from api.protocol.fixture.token import btc_token, sol_token


@fixture
def chain():
    chain = mock.Mock(spec=Chain)
    chain.get_token_decimals.return_value = 10

    return chain


@fixture
def exchange():
    exchange = mock.Mock(spec=Exchange)

    exchange.convert_balance_to_asset.side_effect = (
        lambda taker, balance, asset, investment_parameters: ExchangeConvertedBalance(
            sell_balance=balance,
            buy_balance=BalanceAtomic(
                asset=asset,
                amount=balance.amount * Decimal("10"),
                amount_atomic=balance.amount_atomic * 10,
                decimals=18,
            ),
            fees=Fees(
                gas_fee=None,
                provider_fee=None,
                platform_fee=BalanceAtomic(
                    asset=btc_token,
                    amount=Decimal("0.0000001"),
                    amount_atomic=1,
                    decimals=18,
                ),
            ),
        )
    )

    return exchange


@fixture
def taker():
    return Address("0x1234abcd5678efgh9012ijklmnopqrstuvwx3456")


@fixture
def asset_balance_converter(exchange: Exchange, chain: Chain):
    return AssetBalanceConverter(exchange=exchange, chain=chain)


@mark.asyncio
async def test_asset_balance_converter_sell_basket_to_buy_token(
    asset_balance_converter: AssetBalanceConverter,
    taker: Address,
):
    sell_balance = BalanceAtomic(
        asset=test_basket, amount=Decimal("50"), amount_atomic=50 * 10**18, decimals=18
    )

    convert_asset_balance = await asset_balance_converter.convert(
        taker, sell_balance, sol_token
    )

    assert convert_asset_balance.total_balance == ConvertedBalance(
        sell_balance=BalanceAtomic(
            asset=test_basket,
            amount=Decimal("50"),
            amount_atomic=50 * 10**18,
            decimals=18,
        ),
        buy_balance=BalanceAtomic(
            asset=sol_token,
            amount=Decimal("500"),
            amount_atomic=500 * 10**18,
            decimals=18,
        ),
        fees=Fees(
            gas_fee=None,
            provider_fee=None,
            platform_fee=BalanceAtomic(
                asset=btc_token,
                amount=Decimal("0.0000001"),
                amount_atomic=1,
                decimals=18,
            ),
        ),
    )

    assert convert_asset_balance.balances == []


@mark.asyncio
async def test_asset_balance_converter_buy_basket_to_sell_token(
    asset_balance_converter: AssetBalanceConverter,
    taker: Address,
):
    sell_balance = BalanceAtomic[Token](
        asset=sol_token, amount=Decimal("88"), amount_atomic=88 * 10**18, decimals=18
    )
    convert_asset_balance = await asset_balance_converter.convert(
        taker, sell_balance, test_basket
    )

    assert convert_asset_balance.fees == Fees(
        gas_fee=None,
        provider_fee=None,
        platform_fee=BalanceAtomic(
            asset=btc_token,
            amount=Decimal("0.0000001"),
            amount_atomic=1,
            decimals=18,
        ),
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
            amount=Decimal("880"),
            amount_atomic=880 * 10**18,
            decimals=18,
        ),
        fees=Fees(
            gas_fee=None,
            provider_fee=None,
            platform_fee=BalanceAtomic(
                asset=btc_token,
                amount=Decimal("0.0000001"),
                amount_atomic=1,
                decimals=18,
            ),
        ),
    )
    assert convert_asset_balance.balances == []


@mark.asyncio
async def test_asset_balance_converter_sell_token_to_buy_token(
    asset_balance_converter: AssetBalanceConverter,
    taker: Address,
):
    sell_balance = BalanceAtomic[Token](
        asset=sol_token, amount=Decimal("88"), amount_atomic=88 * 10**18, decimals=18
    )

    convert_asset_balance = await asset_balance_converter.convert(
        taker, sell_balance, btc_token
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
        fees=Fees(
            gas_fee=None,
            provider_fee=None,
            platform_fee=BalanceAtomic(
                asset=btc_token,
                amount=Decimal("0.0000001"),
                amount_atomic=1,
                decimals=18,
            ),
        ),
    )
    assert convert_asset_balance.balances == []
