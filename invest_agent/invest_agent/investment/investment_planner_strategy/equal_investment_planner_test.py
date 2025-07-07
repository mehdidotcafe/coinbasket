from decimal import Decimal
from unittest import mock
from protocol.basket import Basket
from protocol.token import Token
from pytest import fixture, raises, mark
from invest_agent.chain.balance import Balance
from invest_agent.chain.chain import Chain
from invest_agent.investment.exception.insufficient_balance import (
    InsufficientBalance,
)
from invest_agent.investment.investment_planner_strategy.equal_investment_planner import (
    EqualInvestmentPlanner,
)
from invest_agent.investment.investment_plan import (
    InvestmentPlan,
    InvestmentPlanStep,
)
from protocol.fixture.token import bnb_token


@fixture
def chain():
    return mock.Mock(spec=Chain)


@fixture
def sell_token():
    return bnb_token


@fixture
def basket():
    return Basket(
        id="5c1753e1-f94f-4212-9949-1d64e3ad455c",
        name="Test Basket",
        description="A test basket",
        tokens=[
            Token(
                id="bsc:0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
                name="Binance Pegged Bitcoin",
                display_name="Bitcoin",
                ticker="BTC",
                address="0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
            ),
            Token(
                id="bsc:0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
                name="Binance Pegged ETH",
                display_name="Ethereum",
                ticker="ETH",
                address="0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
            ),
        ],
    )


@fixture
def investment_planner(chain: Chain):
    return EqualInvestmentPlanner(chain=chain)


@mark.asyncio
async def test_make_investment_plan(
    investment_planner: EqualInvestmentPlanner,
    basket: Basket,
    chain: Chain,
    sell_token: Token,
):
    chain.get_balance.return_value = Balance(amount=Decimal("1000.0"), token=sell_token)
    chain.get_min_balance.return_value = Balance(amount=Decimal("2"), token=sell_token)

    result = await investment_planner.make_investment_plan(basket)

    chain.get_min_balance.assert_called_once()
    chain.get_balance.assert_called_once()

    assert result == InvestmentPlan(
        steps=[
            InvestmentPlanStep(
                token=basket.tokens[0],
                sell_balance=Balance(token=sell_token, amount=Decimal("499.0")),
            ),
            InvestmentPlanStep(
                token=basket.tokens[1],
                sell_balance=Balance(token=sell_token, amount=Decimal("499.0")),
            ),
        ],
        sell_total_balance=Balance(token=sell_token, amount=Decimal("998.0")),
    )


@mark.asyncio
async def test_make_investment_plan_insufficient_balance(
    investment_planner: EqualInvestmentPlanner,
    basket: Basket,
    chain: Chain,
    sell_token: Token,
):
    chain.get_balance.return_value = Balance(amount=Decimal("1000.0"), token=sell_token)
    chain.get_min_balance.return_value = Balance(
        amount=Decimal("9999.9"), token=sell_token
    )

    with raises(InsufficientBalance):
        await investment_planner.make_investment_plan(basket)
