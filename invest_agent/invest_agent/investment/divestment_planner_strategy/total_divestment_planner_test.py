from decimal import Decimal
from unittest import mock

from invest_agent.investment.basket_investment import BasketInvestment, Bid
from pytest import fixture
from protocol.token import Token
from invest_agent.chain.balance import Balance
from invest_agent.chain.chain import Chain
from invest_agent.investment.divestment_planner_strategy.total_divestment_planner import (
    TotalDivestmentPlanner,
)
from invest_agent.investment.investment_plan import InvestmentPlan, InvestmentPlanStep


@fixture
def chain():
    return mock.Mock(spec=Chain)


def test_make_divestment_plan_success(chain: Chain):
    """Test the divestment plan creation."""
    base_token = Token(
        name="Base Token",
        display_name="Base Token",
        ticker="BTK",
        address="0x123",
    )
    divestment_plan = BasketInvestment(
        name="Test Basket",
        description="A test basket",
        invested_at="2020-05-09",
        type="basket divestment",
        bids=[
            Bid(
                token=Token(
                    name="Test Token",
                    display_name="Test",
                    ticker="TTK",
                    address="0x123",
                ),
                balance_in=Balance(
                    amount=Decimal("100"),
                    token=Token(
                        name="Test Token 1",
                        display_name="Test 1",
                        ticker="TTK1",
                        address="0x1",
                    ),
                ),
                balance_out=Balance(
                    amount=Decimal("200"),
                    token=Token(
                        name="Test Token 2",
                        display_name="Test 2",
                        ticker="TTK2",
                        address="0x2",
                    ),
                ),
            )
        ],
        status="invested",
    )

    chain.get_base_token.return_value = base_token

    divestment_planner = TotalDivestmentPlanner(chain)

    investment_plan = divestment_planner.make_divestment_plan(divestment_plan)

    assert investment_plan == InvestmentPlan(
        steps=[
            InvestmentPlanStep(
                token=Token(
                    name="Test Token 2",
                    display_name="Test 2",
                    ticker="TTK2",
                    address="0x2",
                ),
                amount=Decimal("200"),
            )
        ],
        balance=Balance(
            amount=Decimal("0"),
            token=base_token,
        ),
    )
