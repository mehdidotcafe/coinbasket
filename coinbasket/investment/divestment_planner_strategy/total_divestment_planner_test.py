from decimal import Decimal
from unittest import mock

from pytest import fixture
from coinbasket.basket import Token
from coinbasket.chain.balance import Balance
from coinbasket.chain.chain import Chain
from coinbasket.investment.divestment_planner_strategy.total_divestment_planner import (
    TotalDivestmentPlanner,
)
from coinbasket.investment.investment_plan import InvestmentPlan, InvestmentPlanStep
from coinbasket.investment.investment_result import (
    InvestmentResult,
    InvestmentResultBid,
)


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
    divestment_plan = InvestmentResult(
        bids=[
            InvestmentResultBid(
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
        ]
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
