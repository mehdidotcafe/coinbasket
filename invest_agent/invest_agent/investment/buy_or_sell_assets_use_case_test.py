from decimal import Decimal
from unittest import mock
from invest_agent.chain.balance import Balance
from invest_agent.chain.chain import Chain
from invest_agent.chain.exception.insufficient_balance import InsufficientBalance
from invest_agent.investment.buy_or_sell_assets_use_case import (
    BuyOrSellAssetsUseCase,
)
from invest_agent.investment.exchange.exchange import Exchange
from invest_agent.investment.investment_parameters import InvestmentParameters
from invest_agent.investment.investment_planner.equal_investment_planner import (
    EqualInvestmentPlanner,
)

from invest_agent.investment.investment_planner.investment_plan import (
    InvestmentPlan,
    InvestmentPlanStep,
)
from invest_agent.investment.investment_planner.investment_planner import (
    InvestmentPlanner,
)
from invest_agent.investment.order import Order
from pytest import fixture, raises, mark
from protocol.fixture.token import bnb_token, wbnb_token, eth_token


@fixture
def chain():
    return mock.Mock(spec=Chain)


@fixture
def exchange():
    return mock.Mock(spec=Exchange)


@fixture
def investment_planner():
    return mock.Mock(spec=InvestmentPlanner)


@fixture
def use_case(chain: Chain, exchange: Exchange, investment_planner: InvestmentPlanner):
    return BuyOrSellAssetsUseCase(chain, exchange, investment_planner)


@mark.asyncio
async def test_buy_or_sell_assets_use_case_not_enough_balance_for_gas(
    chain: Chain, use_case: BuyOrSellAssetsUseCase
):
    chain.get_available_balance.side_effect = InsufficientBalance(
        min_balance=Balance(amount=Decimal(0.01), token=bnb_token)
    )

    with raises(InsufficientBalance):
        await use_case.execute([])


@mark.asyncio
async def test_buy_or_sell_assets_use_case_success(
    chain: Chain,
    exchange: Exchange,
    investment_planner: InvestmentPlanner,
    use_case: BuyOrSellAssetsUseCase,
):
    chain.get_available_balance = mock.AsyncMock(
        return_value=Balance(amount=Decimal(1.0), token=bnb_token)
    )
    investment_planner.make_investment_plan.return_value = InvestmentPlan(
        steps=[
            InvestmentPlanStep(
                buy_token=wbnb_token,
                sell_balance=Balance(amount=Decimal(0.5), token=bnb_token),
            ),
            InvestmentPlanStep(
                buy_token=eth_token,
                sell_balance=Balance(amount=Decimal(0.5), token=bnb_token),
            ),
        ]
    )
    exchange.execute_investment_plan = mock.AsyncMock(
        return_value=[
            Order(
                id="order-1",
                sell_balance=Balance(amount=Decimal(0.5), token=bnb_token),
                buy_token=wbnb_token,
                type="BUY",
                tries=[],
                created_at=0,
                status="PENDING",
                trigger="MANUAL",
                basket_id=None,
            ),
            Order(
                id="order-2",
                sell_balance=Balance(amount=Decimal(0.5), token=bnb_token),
                buy_token=eth_token,
                type="BUY",
                tries=[],
                created_at=0,
                status="PENDING",
                trigger="MANUAL",
                basket_id=None,
            ),
        ]
    )

    orders = await use_case.execute([wbnb_token, eth_token])

    chain.get_available_balance.assert_called_once()
    investment_planner.make_investment_plan.assert_called_once_with(
        assets=[wbnb_token, eth_token],
        investment_balance=Balance(amount=Decimal(1.0), token=bnb_token),
    )
    exchange.execute_investment_plan.assert_called_once_with(
        investment_plan=InvestmentPlan(
            steps=[
                InvestmentPlanStep(
                    buy_token=wbnb_token,
                    sell_balance=Balance(amount=Decimal(0.5), token=bnb_token),
                ),
                InvestmentPlanStep(
                    buy_token=eth_token,
                    sell_balance=Balance(amount=Decimal(0.5), token=bnb_token),
                ),
            ]
        ),
        investment_parameters=InvestmentParameters(
            slippage_tolerance_in_percentage=Decimal("1"),
        ),
    )

    assert orders == [
        Order(
            id="order-1",
            sell_balance=Balance(amount=Decimal(0.5), token=bnb_token),
            buy_token=wbnb_token,
            type="BUY",
            tries=[],
            created_at=0,
            status="PENDING",
            trigger="MANUAL",
            basket_id=None,
        ),
        Order(
            id="order-2",
            sell_balance=Balance(amount=Decimal(0.5), token=bnb_token),
            buy_token=eth_token,
            type="BUY",
            tries=[],
            created_at=0,
            status="PENDING",
            trigger="MANUAL",
            basket_id=None,
        ),
    ]
