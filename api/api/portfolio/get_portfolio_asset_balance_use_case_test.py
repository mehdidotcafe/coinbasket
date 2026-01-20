from decimal import Decimal
from unittest import mock
from api.address.address import Address
from api.chain.balance import BalanceAtomic
from api.chain.chain import Chain
from api.portfolio.get_portfolio_asset_balance_use_case import (
    GetPortfolioAssetBalanceUseCase,
    PortfolioAssetBalance,
)
from api.portfolio.holding.holding import Holding
from api.portfolio.holding.holding_repository import HoldingRepository
from pytest import fixture, mark

from api.protocol.fixture.token import bnb_token, eth_token, wbnb_token


@fixture
def chain():
    chain = mock.Mock(spec=Chain)

    chain.get_token_decimals.return_value = 10

    return chain


@fixture
def holding_repository():
    return mock.Mock(spec=HoldingRepository)


@fixture
def address():
    return Address("0x1234567890abcdef1234567890abcdef12345678")


@fixture
def use_case(chain: Chain, holding_repository: HoldingRepository):
    return GetPortfolioAssetBalanceUseCase(chain, holding_repository)


@mark.asyncio
async def test_get_portfolio_asset_balance_use_case_with_native_token(
    address: Address,
    chain: Chain,
    holding_repository: HoldingRepository,
    use_case: GetPortfolioAssetBalanceUseCase,
):
    chain.is_native_token.return_value = True
    chain.get_wrapped_base_token.return_value = wbnb_token
    chain.get_native_token_balance.return_value = BalanceAtomic(
        asset=bnb_token, amount=Decimal("10"), amount_atomic=10 * 10**18, decimals=18
    )
    holding_repository.get_holding_balance.return_value = Holding(
        balance=BalanceAtomic(
            asset=wbnb_token, amount=Decimal("5"), amount_atomic=5 * 10**18, decimals=18
        ),
        children=[],
    )

    portfolio_asset_balance = await use_case.execute(address, bnb_token)

    chain.is_native_token.assert_called_once_with(bnb_token)
    chain.get_native_token_balance.assert_called_once()
    holding_repository.get_holding_balance.assert_called_once_with(address, wbnb_token)

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
    address: Address,
    chain: Chain,
    holding_repository: HoldingRepository,
    use_case: GetPortfolioAssetBalanceUseCase,
):
    chain.is_native_token.return_value = False
    chain.is_wrapped_native_token.return_value = True
    chain.get_wrapped_base_token.return_value = wbnb_token
    chain.get_native_token_balance.return_value = BalanceAtomic(
        asset=bnb_token, amount=Decimal("10"), amount_atomic=10 * 10**18, decimals=18
    )
    holding_repository.get_holding_balance.return_value = Holding(
        balance=BalanceAtomic(
            asset=wbnb_token, amount=Decimal("5"), amount_atomic=5 * 10**18, decimals=18
        ),
        children=[],
    )
    portfolio_asset_balance = await use_case.execute(address, wbnb_token)

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
    address: Address,
    chain: Chain,
    holding_repository: HoldingRepository,
    use_case: GetPortfolioAssetBalanceUseCase,
):
    chain.is_native_token.return_value = False
    chain.is_wrapped_native_token.return_value = False
    holding_repository.get_holding_balance.return_value = Holding(
        balance=BalanceAtomic(
            asset=eth_token,
            amount=Decimal("42"),
            amount_atomic=10 * 10**18,
            decimals=18,
        ),
        children=[],
    )

    asset_balance = await use_case.execute(address, eth_token)

    chain.is_native_token.assert_called_once_with(eth_token)
    holding_repository.get_holding_balance.assert_called_once_with(address, eth_token)

    assert asset_balance == PortfolioAssetBalance(
        holding_balance=BalanceAtomic(
            asset=eth_token,
            amount=Decimal("42"),
            amount_atomic=10 * 10**18,
            decimals=18,
        )
    )
