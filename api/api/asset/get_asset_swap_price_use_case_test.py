from decimal import Decimal
from unittest import mock

from api.address.address import Address
from api.asset.get_asset_swap_price_use_case import (
    AssetSwapPriceInfo,
    GetAssetSwapPriceUseCase,
    ConvertedBalance,
)
from api.chain.balance import BalanceAtomic
from api.chain.chain import Chain
from api.investment.calculator.asset_balance_converter import (
    AssetBalanceConverter,
    ConvertedAssetBalance,
)
from api.investment.fees import Fees
from pytest import fixture, mark
from api.protocol.fixture.token import wbnb_token
from api.protocol.fixture.basket import test_basket


def to_atomic(amount: Decimal) -> int:
    return int(amount * Decimal("1e18"))


@fixture
def chain():
    chain = mock.Mock(spec=Chain)

    return chain


@fixture
def asset_balance_converter():
    return mock.Mock(spec=AssetBalanceConverter)


@fixture
def address():
    return Address("0x1234abcd5678efgh9012ijklmnopqrstuvwx3456")


@fixture
def use_case(
    chain: Chain,
    asset_balance_converter: AssetBalanceConverter,
):
    return GetAssetSwapPriceUseCase(chain, asset_balance_converter)


@mark.asyncio
async def test_get_asset_swap_price_use_case(
    use_case: GetAssetSwapPriceUseCase,
    asset_balance_converter: AssetBalanceConverter,
    address: Address,
):
    asset_swap_price_info = AssetSwapPriceInfo(
        sell_asset=wbnb_token,
        sell_asset_amount=Decimal("1.0"),
        buy_asset=test_basket,
    )

    fees = Fees(
        gas_fee=None,
        provider_fee=None,
        platform_fee=BalanceAtomic(
            asset=wbnb_token,
            amount=Decimal("0.0000001"),
            amount_atomic=to_atomic(Decimal("0.0000001")),
            decimals=18,
        ),
    )

    asset_balance_converter.convert.return_value = ConvertedAssetBalance(
        total_balance=ConvertedBalance(
            sell_balance=BalanceAtomic(
                asset=wbnb_token,
                amount=Decimal("1.0"),
                amount_atomic=to_atomic(Decimal("1.0")),
                decimals=18,
            ),
            buy_balance=BalanceAtomic(
                asset=test_basket,
                amount=Decimal("300.0"),
                amount_atomic=to_atomic(Decimal("300.0")),
                decimals=18,
            ),
            fees=fees,
        ),
        fees=fees,
        balances=[],
    )

    asset_swap_price = await use_case.execute(address, asset_swap_price_info)

    assert asset_swap_price == ConvertedBalance(
        sell_balance=BalanceAtomic(
            asset=wbnb_token,
            amount=Decimal("1.0"),
            amount_atomic=to_atomic(Decimal("1.0")),
            decimals=18,
        ),
        buy_balance=BalanceAtomic(
            asset=test_basket,
            amount=Decimal("300.0"),
            amount_atomic=to_atomic(Decimal("300.0")),
            decimals=18,
        ),
        fees=fees,
    )
