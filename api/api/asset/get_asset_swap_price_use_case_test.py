from decimal import Decimal
from unittest import mock

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
from pytest import fixture, mark
from api.portfolio.holding.holding import Holding
from api.portfolio.posting.posting_repository import PostingRepository
from protocol.fixture.token import wbnb_token
from protocol.fixture.basket import test_basket


def to_atomic(amount: Decimal) -> int:
    return int(amount * Decimal("1e18"))


@fixture
def chain():
    chain = mock.Mock(spec=Chain)

    chain.convert_amount_to_amount_atomic.side_effect = lambda token, amount_readable: (
        int(amount_readable * (10**18)),
        18,
    )
    chain.convert_amount_atomic_to_amount.side_effect = lambda token, amount_atomic: (
        int(amount_atomic / (10**18)),
        18,
    )

    return chain


@fixture
def posting_repository():
    return mock.Mock(spec=PostingRepository)


@fixture
def asset_balance_converter():
    return mock.Mock(spec=AssetBalanceConverter)


@fixture
def use_case(
    chain: Chain,
    posting_repository: PostingRepository,
    asset_balance_converter: AssetBalanceConverter,
):
    return GetAssetSwapPriceUseCase(chain, posting_repository, asset_balance_converter)


@mark.asyncio
async def test_get_asset_swap_price_use_case(
    use_case: GetAssetSwapPriceUseCase,
    posting_repository: PostingRepository,
    asset_balance_converter: AssetBalanceConverter,
):
    asset_swap_price_info = AssetSwapPriceInfo(
        sell_asset=wbnb_token,
        sell_asset_amount=Decimal("1.0"),
        buy_asset=test_basket,
    )

    posting_repository.get_holding_balance.return_value = Holding(
        balance=BalanceAtomic(
            asset=test_basket,
            amount=Decimal("1.0"),
            amount_atomic=to_atomic(Decimal("1.0")),
            decimals=18,
        ),
        children=[],
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
        ),
        balances=[],
    )

    asset_swap_price = await use_case.execute(asset_swap_price_info)

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
    )
