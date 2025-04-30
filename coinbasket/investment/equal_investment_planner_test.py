from decimal import Decimal
from unittest import mock
from pytest import fixture, raises
from coinbasket.basket import Basket, Token
from coinbasket.chain.balance import Balance
from coinbasket.chain.chain import Chain
from coinbasket.investment.insufficient_balance_exception import (
    InsufficientBalanceException,
)
from coinbasket.investment.equal_investment_planner import (
    EqualInvestmentPlanner,
)
from coinbasket.investment.investment_plan import (
    InvestmentPlan,
    InvestmentPlanStep,
)


@fixture
def chain():
    return mock.Mock(spec=Chain)


@fixture
def base_token():
    return Token(name="BNB", display_name="BNB", ticker="BNB", address="")


@fixture
def basket():
    return Basket(
        name="Test Basket",
        tokens=[
            Token(
                name="Binance Pegged Bitcoin",
                display_name="Bitcoin",
                ticker="BTC",
                address="0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
            ),
            Token(
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


def test_make_investment_plan(
    investment_planner: EqualInvestmentPlanner,
    basket: Basket,
    chain: Chain,
    base_token: Token,
):
    chain.get_balance.return_value = Balance(amount=Decimal("1000.0"), token=base_token)
    chain.get_min_balance.return_value = Balance(amount=Decimal("2"), token=base_token)

    result = investment_planner.make_investment_plan(basket)

    chain.get_min_balance.assert_called_once()
    chain.get_balance.assert_called_once()

    assert result == InvestmentPlan(
        steps=[
            InvestmentPlanStep(
                token=basket.tokens[0],
                amount=Decimal("499.0"),
            ),
            InvestmentPlanStep(
                token=basket.tokens[1],
                amount=Decimal("499.0"),
            ),
        ],
        balance=Balance(token=base_token, amount=Decimal("998.0")),
    )


def test_make_investment_plan_insufficient_balance(
    investment_planner: EqualInvestmentPlanner,
    basket: Basket,
    chain: Chain,
    base_token: Token,
):
    chain.get_balance.return_value = Balance(amount=Decimal("1000.0"), token=base_token)
    chain.get_min_balance.return_value = Balance(
        amount=Decimal("9999.9"), token=base_token
    )

    with raises(InsufficientBalanceException):
        investment_planner.make_investment_plan(basket)
