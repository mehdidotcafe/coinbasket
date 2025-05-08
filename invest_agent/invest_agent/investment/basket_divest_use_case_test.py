from decimal import Decimal
from unittest import mock
from pytest import fixture

from protocol.token import Token
from invest_agent.chain.balance import Balance
from invest_agent.investment.basket_divest_use_case import BasketDivestUseCase
from invest_agent.investment.divestment_planner import DivestmentPlanner
from invest_agent.investment.exchange.exchange import Exchange
from invest_agent.investment.investment_plan import InvestmentPlan, InvestmentPlanStep
from invest_agent.investment.investment_result import (
    InvestmentResult,
    InvestmentResultBid,
)
from invest_agent.storage.storage import Storage


@fixture
def divestment_planner():
    return mock.Mock(spec=DivestmentPlanner)


@fixture
def exchange():
    return mock.Mock(spec=Exchange)


@fixture
def storage():
    return mock.Mock(spec=Storage)


def test_basket_divest_use_case_execute_no_investment(
    divestment_planner: DivestmentPlanner,
    exchange: Exchange,
    storage: Storage[InvestmentResult],
):
    storage.get.return_value = None

    use_case = BasketDivestUseCase(divestment_planner, exchange, storage)

    message, result = use_case.execute()

    assert message == "Divestment error: No investment basket found."
    assert result is None

    storage.get.assert_called_once_with("investment_result")


def test_basket_divest_use_case_execute_exception(
    divestment_planner: DivestmentPlanner,
    exchange: Exchange,
    storage: Storage[InvestmentResult],
):
    divestment_plan = InvestmentPlan(
        steps=[
            InvestmentPlanStep(
                token=Token(
                    name="Test Token 1",
                    display_name="Test 1",
                    ticker="TTK1",
                    address="0x1",
                ),
                amount=Decimal("100"),
            ),
            InvestmentPlanStep(
                token=Token(
                    name="Test Token 2",
                    display_name="Test 2",
                    ticker="TTK2",
                    address="0x2",
                ),
                amount=Decimal("200"),
            ),
        ],
        balance=Balance(
            amount=Decimal("0"),
            token=Token(
                name="Test Token",
                display_name="Test",
                ticker="TTK",
                address="0x123",
            ),
        ),
    )
    investment_result = InvestmentResult(
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
    storage.get.return_value = [investment_result, 1]
    divestment_planner.make_divestment_plan.return_value = divestment_plan

    exchange.execute_divestment_plan.side_effect = Exception("Error")

    use_case = BasketDivestUseCase(divestment_planner, exchange, storage)

    message, result = use_case.execute()

    assert message == "Divestment error: Error"
    assert result is None


def test_basket_divest_use_case_execute_success(
    divestment_planner: DivestmentPlanner,
    exchange: Exchange,
    storage: Storage[InvestmentResult],
):
    investment_result = InvestmentResult(
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
    divestment_plan = InvestmentPlan(
        steps=[
            InvestmentPlanStep(
                token=Token(
                    name="Test Token 1",
                    display_name="Test 1",
                    ticker="TTK1",
                    address="0x1",
                ),
                amount=Decimal("100"),
            ),
            InvestmentPlanStep(
                token=Token(
                    name="Test Token 2",
                    display_name="Test 2",
                    ticker="TTK2",
                    address="0x2",
                ),
                amount=Decimal("200"),
            ),
        ],
        balance=Balance(
            amount=Decimal("0"),
            token=Token(
                name="Test Token",
                display_name="Test",
                ticker="TTK",
                address="0x123",
            ),
        ),
    )
    divestment_result = InvestmentResult(
        bids=[
            InvestmentResultBid(
                token=Token(
                    name="WBNB",
                    display_name="WBNB",
                    ticker="WBNB",
                    address="0x238928933434",
                ),
                balance_in=Balance(
                    amount=Decimal("200"),
                    token=Token(
                        name="Test Token",
                        display_name="Test",
                        ticker="TTK",
                        address="0x123",
                    ),
                ),
                balance_out=Balance(
                    amount=Decimal("100"),
                    token=Token(
                        name="WBNB",
                        display_name="WBNB",
                        ticker="WBNB",
                        address="0x238928933434",
                    ),
                ),
            )
        ]
    )

    storage.get.return_value = [investment_result, 1]
    divestment_planner.make_divestment_plan.return_value = divestment_plan
    exchange.execute_divestment_plan.return_value = divestment_result

    use_case = BasketDivestUseCase(divestment_planner, exchange, storage)

    message, result = use_case.execute()

    assert message == "Divestment success."
    assert result == divestment_result

    storage.get.assert_called_once_with("investment_result")
    divestment_planner.make_divestment_plan.assert_called_once_with(investment_result)
    exchange.execute_divestment_plan.assert_called_once_with(divestment_plan)
    storage.remove.assert_called_once_with("investment_result")
