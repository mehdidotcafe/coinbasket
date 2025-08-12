from decimal import Decimal
from unittest import mock

from invest_agent.asset.get_asset_swap_price_use_case import (
    AssetSwapPriceInfo,
    GetAssetSwapPriceUseCase,
)
from invest_agent.chain.balance import BalanceAtomic
from invest_agent.chain.chain import Chain
from invest_agent.investment.exception.cannot_swap_basket_for_another_exception import (
    CannotSwapBasketForAnotherException,
)
from invest_agent.investment.exchange.exchange import ConvertedBalance, Exchange
from invest_agent.investment.investment_parameters import InvestmentParameters
from pytest import fixture, mark, raises
from protocol.fixture.token import wbnb_token, usdt_token
from protocol.fixture.basket import big4_basket


def to_atomic(amount: Decimal) -> int:
    return int(amount * Decimal("1e18"))


@fixture
def exchange():
    return mock.Mock(spec=Exchange)


@fixture
def chain():
    chain = mock.Mock(spec=Chain)

    chain.convert_amount_to_amount_atomic.side_effect = (
        lambda token, amount_readable: int(amount_readable * (10**18))
    )
    chain.convert_amount_atomic_to_amount.side_effect = (
        lambda token, amount_atomic: int(amount_atomic / (10**18))
    )

    return chain


@fixture
def use_case(exchange: Exchange, chain: Chain):
    return GetAssetSwapPriceUseCase(exchange, chain)


@mark.asyncio
async def test_get_asset_swap_price_use_case_sell_token_buy_token(
    use_case: GetAssetSwapPriceUseCase, exchange: Exchange
):
    asset_swap_price_info = AssetSwapPriceInfo(
        sell_asset=wbnb_token,
        sell_asset_amount=Decimal("1.0"),
        buy_asset=usdt_token,
    )

    exchange.convert_balance_to_token.return_value = ConvertedBalance(
        sell_balance=BalanceAtomic(
            asset=wbnb_token,
            amount=Decimal("1.0"),
            amount_atomic=to_atomic(Decimal("1.0")),
        ),
        buy_balance=BalanceAtomic(
            asset=usdt_token,
            amount=Decimal("300.0"),
            amount_atomic=to_atomic(Decimal("300.0")),
        ),
    )

    asset_swap_price = await use_case.execute(asset_swap_price_info)

    exchange.convert_balance_to_token.assert_called_once_with(
        balance=BalanceAtomic(
            asset=wbnb_token,
            amount=Decimal("1.0"),
            amount_atomic=to_atomic(Decimal("1.0")),
        ),
        token=usdt_token,
        investment_parameters=InvestmentParameters(
            slippage_tolerance_in_percentage=Decimal("1"),
        ),
    )

    assert asset_swap_price == ConvertedBalance(
        sell_balance=BalanceAtomic(
            asset=wbnb_token,
            amount=Decimal("1.0"),
            amount_atomic=to_atomic(Decimal("1.0")),
        ),
        buy_balance=BalanceAtomic(
            asset=usdt_token,
            amount=Decimal("300.0"),
            amount_atomic=to_atomic(Decimal("300.0")),
        ),
    )


@mark.asyncio
async def test_get_asset_swap_price_use_case_buy_basket_sell_token(
    use_case: GetAssetSwapPriceUseCase, exchange: Exchange
):
    asset_swap_price_info = AssetSwapPriceInfo(
        sell_asset=wbnb_token,
        sell_asset_amount=Decimal("1.0"),
        buy_asset=big4_basket,
    )

    exchange.convert_balance_to_token.return_value = ConvertedBalance(
        sell_balance=BalanceAtomic(
            asset=wbnb_token,
            amount=Decimal("1.0"),
            amount_atomic=to_atomic(Decimal("1.0")),
        ),
        buy_balance=BalanceAtomic(
            asset=usdt_token,
            amount=Decimal("3000.0"),
            amount_atomic=to_atomic(Decimal("3000.0")),
        ),
    )

    asset_swap_price = await use_case.execute(asset_swap_price_info)

    exchange.convert_balance_to_token.assert_called_once_with(
        balance=BalanceAtomic(
            asset=wbnb_token,
            amount=Decimal("1.0"),
            amount_atomic=to_atomic(Decimal("1.0")),
        ),
        token=usdt_token,
        investment_parameters=InvestmentParameters(
            slippage_tolerance_in_percentage=Decimal("1"),
        ),
    )

    assert asset_swap_price == ConvertedBalance(
        sell_balance=BalanceAtomic(
            asset=wbnb_token,
            amount=Decimal("1.0"),
            amount_atomic=to_atomic(Decimal("1.0")),
        ),
        buy_balance=BalanceAtomic(
            asset=big4_basket,
            amount=Decimal("300.0"),
            amount_atomic=to_atomic(Decimal("300.0")),
        ),
    )


@mark.asyncio
async def test_get_asset_swap_price_use_case_sell_basket_buy_token(
    use_case: GetAssetSwapPriceUseCase, exchange: Exchange
):
    asset_swap_price_info = AssetSwapPriceInfo(
        sell_asset=big4_basket,
        sell_asset_amount=Decimal("50.0"),
        buy_asset=wbnb_token,
    )

    exchange.convert_balance_to_token.return_value = ConvertedBalance(
        sell_balance=BalanceAtomic(
            asset=usdt_token,
            amount=Decimal("50.0"),
            amount_atomic=to_atomic(Decimal("50.0")),
        ),
        buy_balance=BalanceAtomic(
            asset=wbnb_token,
            amount=Decimal("60.0"),
            amount_atomic=to_atomic(Decimal("60.0")),
        ),
    )

    asset_swap_price = await use_case.execute(asset_swap_price_info)

    exchange.convert_balance_to_token.assert_called_once_with(
        balance=BalanceAtomic(
            asset=usdt_token,
            amount=Decimal("500.0"),
            amount_atomic=to_atomic(Decimal("500.0")),
        ),
        token=wbnb_token,
        investment_parameters=InvestmentParameters(
            slippage_tolerance_in_percentage=Decimal("1"),
        ),
    )

    assert asset_swap_price == ConvertedBalance(
        buy_balance=BalanceAtomic(
            asset=wbnb_token,
            amount=Decimal("60.0"),
            amount_atomic=to_atomic(Decimal("60.0")),
        ),
        sell_balance=BalanceAtomic(
            asset=big4_basket,
            amount=Decimal("50.0"),
            amount_atomic=to_atomic(Decimal("50.0")),
        ),
    )


@mark.asyncio
async def test_get_asset_swap_price_use_case_cannot_swap_basket_for_another(
    use_case: GetAssetSwapPriceUseCase,
):
    asset_swap_price_info = AssetSwapPriceInfo(
        sell_asset=big4_basket,
        sell_asset_amount=Decimal("50.0"),
        buy_asset=big4_basket,
    )

    with raises(CannotSwapBasketForAnotherException):
        await use_case.execute(asset_swap_price_info)
