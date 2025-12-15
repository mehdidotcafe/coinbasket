from decimal import Decimal
from unittest import mock
from api.chain.balance import BalanceAtomic
from api.chain.chain import Chain
from api.portfolio.get_portfolio_asset_balance_use_case import (
    GetPortfolioAssetBalanceUseCase,
    PortfolioAssetBalance,
)
from api.portfolio.holding.holding import Holding
from api.portfolio.posting.posting_repository import PostingRepository
from pytest import fixture, mark

from api.protocol.fixture.token import bnb_token, eth_token, wbnb_token


@fixture
def chain():
    chain = mock.Mock(spec=Chain)

    chain.get_token_decimals.return_value = 10

    return chain


@fixture
def posting_repository():
    return mock.Mock(spec=PostingRepository)


@fixture
def use_case(chain: Chain, posting_repository: PostingRepository):
    return GetPortfolioAssetBalanceUseCase(chain, posting_repository)


@mark.asyncio
async def test_get_portfolio_asset_balance_use_case_with_native_token(
    chain: Chain,
    posting_repository: PostingRepository,
    use_case: GetPortfolioAssetBalanceUseCase,
):
    chain.is_native_token.return_value = True
    chain.get_wrapped_base_token.return_value = wbnb_token
    chain.get_native_token_balance.return_value = BalanceAtomic(
        asset=bnb_token, amount=Decimal("10"), amount_atomic=10 * 10**18, decimals=18
    )
    posting_repository.get_holding_balance.return_value = Holding(
        balance=BalanceAtomic(
            asset=wbnb_token, amount=Decimal("5"), amount_atomic=5 * 10**18, decimals=18
        ),
        children=[],
    )

    portfolio_asset_balance = await use_case.execute(bnb_token)

    chain.is_native_token.assert_called_once_with(bnb_token)
    chain.get_native_token_balance.assert_called_once()
    posting_repository.get_holding_balance.assert_called_once_with(wbnb_token, 10)

    assert portfolio_asset_balance == PortfolioAssetBalance(
        holding_balance=BalanceAtomic(
            asset=wbnb_token, amount=Decimal("5"), amount_atomic=5 * 10**18, decimals=18
        ),
        available_balance=BalanceAtomic(
            asset=bnb_token,
            amount=Decimal("10"),
            amount_atomic=10 * 10**18,
            decimals=18,
        ),
    )


@mark.asyncio
async def test_get_portfolio_asset_balance_use_case_with_wrapped_native_token(
    chain: Chain,
    posting_repository: PostingRepository,
    use_case: GetPortfolioAssetBalanceUseCase,
):
    chain.is_native_token.return_value = False
    chain.is_wrapped_native_token.return_value = True
    chain.get_wrapped_base_token.return_value = wbnb_token
    chain.get_native_token_balance.return_value = BalanceAtomic(
        asset=bnb_token, amount=Decimal("10"), amount_atomic=10 * 10**18, decimals=18
    )
    posting_repository.get_holding_balance.return_value = Holding(
        balance=BalanceAtomic(
            asset=wbnb_token, amount=Decimal("5"), amount_atomic=5 * 10**18, decimals=18
        ),
        children=[],
    )
    portfolio_asset_balance = await use_case.execute(wbnb_token)

    chain.is_wrapped_native_token.assert_called_once_with(wbnb_token)

    assert portfolio_asset_balance == PortfolioAssetBalance(
        holding_balance=BalanceAtomic(
            asset=wbnb_token, amount=Decimal("5"), amount_atomic=5 * 10**18, decimals=18
        ),
        available_balance=BalanceAtomic(
            asset=bnb_token,
            amount=Decimal("10"),
            amount_atomic=10 * 10**18,
            decimals=18,
        ),
    )


@mark.asyncio
async def test_get_portfolio_asset_balance_use_case_with_token(
    chain: Chain,
    posting_repository: PostingRepository,
    use_case: GetPortfolioAssetBalanceUseCase,
):
    chain.is_native_token.return_value = False
    chain.is_wrapped_native_token.return_value = False
    posting_repository.get_holding_balance.return_value = Holding(
        balance=BalanceAtomic(
            asset=eth_token,
            amount=Decimal("42"),
            amount_atomic=10 * 10**18,
            decimals=18,
        ),
        children=[],
    )

    asset_balance = await use_case.execute(eth_token)

    chain.is_native_token.assert_called_once_with(eth_token)
    posting_repository.get_holding_balance.assert_called_once_with(eth_token, 10)

    assert asset_balance == PortfolioAssetBalance(
        holding_balance=BalanceAtomic(
            asset=eth_token,
            amount=Decimal("42"),
            amount_atomic=10 * 10**18,
            decimals=18,
        )
    )
