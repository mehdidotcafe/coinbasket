from decimal import Decimal
from unittest import mock
from invest_agent.chain.balance import BalanceAtomic
from invest_agent.chain.chain import Chain
from invest_agent.investment.exchange.exchange import ExchangeConvertedBalance, Exchange
from invest_agent.investment.investment_parameters import InvestmentParameters
from invest_agent.investment.order.order import Order
from invest_agent.investment.order.order_repository import OrderRepository
from invest_agent.portfolio.posting.posting_repository import (
    PostingRepository,
)
from invest_agent.portfolio.get_portfolio_use_case import (
    GetPortfolioUseCase,
    PortfolioBalance,
)
from pytest import fixture, mark

from protocol.fixture.token import (
    bnb_token,
    eth_token,
    sol_token,
    wbnb_token,
    usdt_token,
)


@fixture
def order_repository():
    return mock.Mock(spec=OrderRepository)


@fixture
def posting_repository():
    return mock.Mock(spec=PostingRepository)


@fixture
def exchange():
    return mock.Mock(spec=Exchange)


@fixture
def chain():
    return mock.Mock(spec=Chain)


@fixture
def investment_parameters():
    return InvestmentParameters(
        slippage_tolerance_in_percentage=Decimal("1"),
    )


@fixture
def use_case(
    order_repository: OrderRepository,
    posting_repository: PostingRepository,
    exchange: Exchange,
    chain: Chain,
):
    return GetPortfolioUseCase(order_repository, posting_repository, exchange, chain)


@mark.asyncio
async def test_get_portfolio_use_case_only_available_balance(
    use_case: GetPortfolioUseCase,
    chain: Chain,
    exchange: Exchange,
    investment_parameters: InvestmentParameters,
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

    portfolio = await use_case.execute(usdt_token)

    chain.get_native_token_balance.assert_called_once()
    exchange.convert_balance_to_token.assert_called_once_with(
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
    use_case: GetPortfolioUseCase, order_repository: OrderRepository
):
    orders = [
        Order(
            id="1",
            sell_balance=BalanceAtomic(
                asset=bnb_token,
                amount=Decimal("1.0"),
                amount_atomic=1 * 10**18,
                decimals=18,
            ),
            buy_balance=BalanceAtomic(
                asset=eth_token,
                amount=Decimal("0.85"),
                amount_atomic=85 * 10**16,
                decimals=18,
            ),
            type="BUY",
            asset_type="TOKEN",
            tries=[],
            created_at=0,
            status="PENDING",
            trigger="MANUAL",
        ),
        Order(
            id="2",
            sell_balance=BalanceAtomic(
                asset=bnb_token,
                amount=Decimal("1.0"),
                amount_atomic=1 * 10**18,
                decimals=18,
            ),
            buy_balance=BalanceAtomic(
                asset=sol_token,
                amount=Decimal("4"),
                amount_atomic=4 * 10**18,
                decimals=18,
            ),
            type="BUY",
            asset_type="TOKEN",
            tries=[],
            created_at=0,
            status="PENDING",
            trigger="MANUAL",
        ),
    ]

    order_repository.get_pending_orders.return_value = orders

    portfolio = await use_case.execute(usdt_token)

    order_repository.get_pending_orders.assert_called_once()

    assert portfolio.pending_orders == orders


@mark.asyncio
async def test_get_portfolio_use_case_holding_balances(
    use_case: GetPortfolioUseCase,
    posting_repository: PostingRepository,
    exchange: Exchange,
    investment_parameters: InvestmentParameters,
):
    holding_balances = [
        BalanceAtomic(
            asset=wbnb_token,
            amount=Decimal("1.0"),
            amount_atomic=1 * 10**18,
            decimals=18,
        ),
        BalanceAtomic(
            asset=sol_token, amount=Decimal("4"), amount_atomic=4 * 10**18, decimals=18
        ),
        BalanceAtomic(
            asset=eth_token,
            amount=Decimal("0.85"),
            amount_atomic=85 * 10**16,
            decimals=18,
        ),
    ]

    posting_repository.get_holding_balances.return_value = holding_balances
    exchange.convert_balance_to_token.side_effect = [
        ExchangeConvertedBalance(
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
        ExchangeConvertedBalance(
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
        ExchangeConvertedBalance(
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

    portfolio = await use_case.execute(usdt_token)

    posting_repository.get_holding_balances.assert_called_once()
    exchange.assert_has_calls(
        [
            mock.call.convert_balance_to_token(
                balance=BalanceAtomic(
                    asset=wbnb_token,
                    amount=Decimal("1.0"),
                    amount_atomic=1 * 10**18,
                    decimals=18,
                ),
                token=usdt_token,
                investment_parameters=investment_parameters,
            ),
            mock.call.convert_balance_to_token(
                balance=BalanceAtomic(
                    asset=sol_token,
                    amount=Decimal("4"),
                    amount_atomic=4 * 10**18,
                    decimals=18,
                ),
                token=usdt_token,
                investment_parameters=investment_parameters,
            ),
            mock.call.convert_balance_to_token(
                balance=BalanceAtomic(
                    asset=eth_token,
                    amount=Decimal("0.85"),
                    amount_atomic=85 * 10**16,
                    decimals=18,
                ),
                token=usdt_token,
                investment_parameters=investment_parameters,
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
        PortfolioBalance(
            native_balance=BalanceAtomic(
                asset=eth_token,
                amount=Decimal("0.85"),
                amount_atomic=85 * 10**16,
                decimals=18,
            ),
            converted_balance=BalanceAtomic(
                asset=usdt_token,
                amount=Decimal("3956"),
                amount_atomic=3956 * 10**18,
                decimals=18,
            ),
        ),
    ]


@mark.asyncio
async def test_get_portfolio_use_case_total_balance(
    use_case: GetPortfolioUseCase,
    posting_repository: PostingRepository,
    exchange: Exchange,
    chain: Chain,
):
    holding_balances = [
        BalanceAtomic(
            asset=eth_token,
            amount=Decimal("0.85"),
            amount_atomic=85 * 10**16,
            decimals=18,
        ),
    ]

    chain.get_native_token_balance.return_value = BalanceAtomic(
        asset=bnb_token,
        amount=Decimal("1000"),
        amount_atomic=1000 * 10**18,
        decimals=18,
    )
    chain.get_token_decimals.return_value = 18
    posting_repository.get_holding_balances.return_value = holding_balances
    exchange.convert_balance_to_token.side_effect = [
        ExchangeConvertedBalance(
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

    portfolio = await use_case.execute(usdt_token)

    assert portfolio.total_balance == BalanceAtomic(
        asset=usdt_token,
        amount=Decimal("803956"),
        amount_atomic=803956 * 10**18,
        decimals=18,
    )
