from decimal import Decimal
from unittest import mock
from pytest import fixture

from invest_agent.basket import Basket, Token
from invest_agent.chain.balance import Balance
from invest_agent.investment.exchange.exchange import Exchange
from invest_agent.investment.investment_planner_strategy.insufficient_balance_exception import (
    InsufficientBalanceException,
)
from invest_agent.investment.basket_invest_use_case import BasketInvestUseCase
from invest_agent.investment.investment_plan import InvestmentPlan, InvestmentPlanStep
from invest_agent.investment.investment_planner import InvestmentPlanner
from invest_agent.investment.investment_result import (
    InvestmentResult,
    InvestmentResultBid,
)
from invest_agent.storage.storage import Storage


@fixture
def investment_planner():
    return mock.Mock(spec=InvestmentPlanner)


@fixture
def exchange():
    return mock.Mock(spec=Exchange)


@fixture
def storage():
    return mock.Mock(spec=Storage)


@fixture
def basket():
    return Basket(
        name="Test Basket",
        tokens=[
            Token(
                name="TokenA",
                display_name="Token A",
                ticker="TKA",
                address="0x1234567890abcdef1234567890abcdef12345678",
            ),
            Token(
                name="TokenB",
                display_name="Token B",
                ticker="TKB",
                address="0xabcdef1234567890abcdef1234567890abcdef12",
            ),
        ],
    )


@fixture
def investment_use_case(
    investment_planner: InvestmentPlanner,
    exchange: Exchange,
    storage: Storage[InvestmentResult],
):
    return BasketInvestUseCase(investment_planner, exchange, storage)


def test_invest_use_case_execute_success(
    investment_use_case: BasketInvestUseCase,
    investment_planner: InvestmentPlanner,
    exchange: Exchange,
    storage: Storage[InvestmentResult],
    basket: Basket,
):
    investment_plan = InvestmentPlan(
        steps=[
            InvestmentPlanStep(
                token=Token(
                    name="TokenA",
                    display_name="Token A",
                    ticker="TKA",
                    address="0x1234567890abcdef1234567890abcdef12345678",
                ),
                amount=Decimal("100"),
            )
        ],
        balance=Balance(
            amount=Decimal("100"),
            token=Token(
                name="Base Token",
                display_name="Base",
                ticker="BASE",
                address="0xabcdef1234567890abcdef1234567890abcdef12",
            ),
        ),
    )
    investment_result = InvestmentResult(
        bids=[
            InvestmentResultBid(
                token=Token(
                    name="TokenA",
                    display_name="Token A",
                    ticker="TKA",
                    address="0x1234567890abcdef1234567890abcdef12345678",
                ),
                balance_in=Balance(
                    amount=Decimal("100"),
                    token=Token(
                        name="Base Token",
                        display_name="Base",
                        ticker="BASE",
                        address="0xabcdef1234567890abcdef1234567890abcdef12",
                    ),
                ),
                balance_out=Balance(
                    amount=Decimal("200"),
                    token=Token(
                        name="TokenA",
                        display_name="Token A",
                        ticker="TKA",
                        address="0x1234567890abcdef1234567890abcdef12345678",
                    ),
                ),
            )
        ]
    )

    investment_planner.make_investment_plan.return_value = investment_plan
    exchange.execute_investment_plan.return_value = investment_result

    message, result = investment_use_case.execute(basket)

    assert message == "Investment success."
    assert result == investment_result

    investment_planner.make_investment_plan.assert_called_once_with(basket)
    exchange.execute_investment_plan.assert_called_once_with(investment_plan)
    storage.set.assert_called_once_with("investment_result", investment_result, 1)


def test_invest_use_case_execute_insufficient_balance(
    investment_use_case: BasketInvestUseCase,
    investment_planner: InvestmentPlanner,
    exchange: Exchange,
    storage: Storage[InvestmentResult],
    basket: Basket,
):
    exception = InsufficientBalanceException(
        Balance(
            amount=Decimal("0"),
            token=Token(
                name="Base Token",
                display_name="Base",
                ticker="BASE",
                address="0xabcdef1234567890abcdef1234567890abcdef12",
            ),
        )
    )

    investment_planner.make_investment_plan.side_effect = exception
    message, result = investment_use_case.execute(basket)

    assert message == exception.message
    assert result is None

    investment_planner.make_investment_plan.assert_called_once_with(basket)
    exchange.execute_investment_plan.assert_not_called()
    storage.set.assert_not_called()
