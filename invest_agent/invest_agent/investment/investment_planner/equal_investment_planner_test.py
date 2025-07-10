from decimal import Decimal
from unittest import mock
from protocol.basket import Basket
from protocol.token import Token
from pytest import fixture, raises, mark
from invest_agent.chain.balance import Balance
from invest_agent.chain.chain import Chain
from invest_agent.investment.investment_planner.equal_investment_planner import (
    EqualInvestmentPlanner,
)
from invest_agent.investment.investment_planner.investment_plan import (
    InvestmentPlan,
    InvestmentPlanStep,
)
from protocol.fixture.token import bnb_token, btc_token, eth_token, sol_token


@fixture
def chain():
    return mock.Mock(spec=Chain)


@fixture
def basket():
    return Basket(
        id="5c1753e1-f94f-4212-9949-1d64e3ad455c",
        name="Test Basket",
        description="A test basket",
        tokens=[
            btc_token,
            eth_token,
        ],
    )


@fixture
def investment_planner():
    return EqualInvestmentPlanner()


def test_make_investment_plan_with_tokens(
    investment_planner: EqualInvestmentPlanner,
):
    result = investment_planner.make_investment_plan(
        [btc_token, sol_token], Balance(token=bnb_token, amount=Decimal("1000.0"))
    )

    assert result == InvestmentPlan(
        steps=[
            InvestmentPlanStep(
                buy_token=btc_token,
                sell_balance=Balance(token=bnb_token, amount=Decimal("500.0")),
                basket=None,
            ),
            InvestmentPlanStep(
                buy_token=sol_token,
                sell_balance=Balance(token=bnb_token, amount=Decimal("500.0")),
                basket=None,
            ),
        ],
    )


def test_make_investment_plan_with_basket(
    investment_planner: EqualInvestmentPlanner,
    basket: Basket,
):
    result = investment_planner.make_investment_plan(
        [basket], Balance(token=bnb_token, amount=Decimal("1000.0"))
    )

    assert result == InvestmentPlan(
        steps=[
            InvestmentPlanStep(
                buy_token=btc_token,
                sell_balance=Balance(token=bnb_token, amount=Decimal("500.0")),
                basket=basket,
            ),
            InvestmentPlanStep(
                buy_token=eth_token,
                sell_balance=Balance(token=bnb_token, amount=Decimal("500.0")),
                basket=basket,
            ),
        ],
    )


def test_make_investment_plan_with_tokens_and_basket(
    investment_planner: EqualInvestmentPlanner, basket: Basket
):
    result = investment_planner.make_investment_plan(
        [btc_token, sol_token, basket],
        Balance(token=bnb_token, amount=Decimal("1000.0")),
    )

    assert result == InvestmentPlan(
        steps=[
            InvestmentPlanStep(
                buy_token=btc_token,
                sell_balance=Balance(token=bnb_token, amount=Decimal("333.33")),
                basket=None,
            ),
            InvestmentPlanStep(
                buy_token=sol_token,
                sell_balance=Balance(token=bnb_token, amount=Decimal("333.33")),
                basket=None,
            ),
            InvestmentPlanStep(
                buy_token=btc_token,
                sell_balance=Balance(token=bnb_token, amount=Decimal("166.66")),
                basket=basket,
            ),
            InvestmentPlanStep(
                buy_token=eth_token,
                sell_balance=Balance(token=bnb_token, amount=Decimal("166.66")),
                basket=basket,
            ),
        ],
    )
