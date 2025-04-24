from unittest import mock
from pytest import fixture, raises
from coinbasket.basket import Basket
from coinbasket.chain.balance import Balance
from coinbasket.chain.chain import Chain
from coinbasket.investment_planner.insufficient_balance_exception import (
    InsufficientBalanceException,
)
from coinbasket.investment_planner.equal_investment_planner import (
    EqualInvestmentPlanner,
)
from coinbasket.investment_planner.investment_plan import (
    InvestmentPlan,
    InvestmentPlanStep,
)


@fixture
def chain():
    return mock.Mock(spec=Chain)


@fixture
def basket():
    return Basket(
        name="Test Basket",
        tokens=[
            {
                "name": "Binance Pegged Bitcoin",
                "displayName": "Bitcoin",
                "ticker": "BTC",
                "address": "0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
            },
            {
                "name": "Binance Pegged ETH",
                "displayName": "Ethereum",
                "ticker": "ETH",
                "address": "0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
            },
        ],
    )


@fixture
def investment_planner(chain: Chain):
    return EqualInvestmentPlanner(chain=chain)


def test_make_investment_plan(
    investment_planner: EqualInvestmentPlanner, basket: Basket, chain: Chain
):
    chain.get_balance.return_value = Balance(amount=1000.0, currency="BNB")
    chain.get_min_balance.return_value = Balance(amount=0.0001, currency="BNB")

    result = investment_planner.make_investment_plan(basket)

    chain.get_min_balance.assert_called_once()
    chain.get_balance.assert_called_once()

    assert result == InvestmentPlan(
        steps=[
            InvestmentPlanStep(
                token=basket.tokens[0],
                amount=500.0,
            ),
            InvestmentPlanStep(
                token=basket.tokens[1],
                amount=500.0,
            ),
        ],
        total_amount=1000.0,
    )


def test_make_investment_plan_insufficient_balance(
    investment_planner: EqualInvestmentPlanner, basket: Basket, chain: Chain
):
    chain.get_balance.return_value = Balance(amount=1000.0, currency="BNB")
    chain.get_min_balance.return_value = Balance(amount=9999.9, currency="BNB")

    with raises(InsufficientBalanceException):
        investment_planner.make_investment_plan(basket)
