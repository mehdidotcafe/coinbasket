from decimal import Decimal
from unittest import mock
from invest_agent.datetime.date_time import DateTime
from invest_agent.investment.basket_investment import BasketInvestment, Bid
from invest_agent.investment.exception.basked_already_invested import (
    BasketAlreadyInvested,
)
from invest_agent.investment.investment_parameters import InvestmentParameters
from protocol.basket import Basket
from protocol.token import Token
from pytest import fixture, raises

from invest_agent.chain.balance import Balance
from invest_agent.investment.exchange.exchange import Exchange
from invest_agent.investment.exception.insufficient_balance import (
    InsufficientBalance,
)
from invest_agent.investment.basket_invest_use_case import BasketInvestUseCase
from invest_agent.investment.investment_plan import InvestmentPlan, InvestmentPlanStep
from invest_agent.investment.investment_planner import InvestmentPlanner
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
def date_time():
    return mock.Mock(spec=DateTime)


@fixture
def basket():
    return Basket(
        name="Test Basket",
        description="A test basket",
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
    storage: Storage[BasketInvestment],
    date_time: DateTime,
):
    return BasketInvestUseCase(investment_planner, exchange, storage, date_time)


def test_invest_use_case_execute_success(
    investment_use_case: BasketInvestUseCase,
    investment_planner: InvestmentPlanner,
    exchange: Exchange,
    storage: Storage[BasketInvestment],
    date_time: DateTime,
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
    basket_investment = BasketInvestment(
        name="Test Basket",
        description="A test basket",
        invested_at="2020-05-09",
        type="basket investment",
        bids=[
            Bid(
                token=Token(
                    name="TokenA",
                    display_name="Token A",
                    ticker="TKA",
                    address="0x1234567890abcdef1234567890abcdef12345678",
                ),
                sell_balance=Balance(
                    amount=Decimal("100"),
                    token=Token(
                        name="Base Token",
                        display_name="Base",
                        ticker="BASE",
                        address="0xabcdef1234567890abcdef1234567890abcdef12",
                    ),
                ),
                buy_balance=Balance(
                    amount=Decimal("200"),
                    token=Token(
                        name="TokenA",
                        display_name="Token A",
                        ticker="TKA",
                        address="0x1234567890abcdef1234567890abcdef12345678",
                    ),
                ),
            )
        ],
        status="invested",
    )

    storage.has.return_value = False
    investment_planner.make_investment_plan.return_value = investment_plan
    exchange.execute_investment_plan.return_value = basket_investment.bids
    date_time.now_str.return_value = "2020-05-09"

    message, result = investment_use_case.execute(basket)

    assert message == "Investment success."
    assert result == basket_investment

    storage.has.assert_called_once_with("basket_investment")
    investment_planner.make_investment_plan.assert_called_once_with(basket)
    exchange.execute_investment_plan.assert_called_once_with(
        investment_plan,
        InvestmentParameters(
            slippage_tolerance_in_percentage=Decimal("1"),
        ),
    )
    storage.set.assert_called_once_with("basket_investment", basket_investment, 1)
    date_time.now_str.assert_called_once()


def test_invest_use_case_execute_insufficient_balance(
    investment_use_case: BasketInvestUseCase,
    investment_planner: InvestmentPlanner,
    exchange: Exchange,
    storage: Storage[BasketInvestment],
    basket: Basket,
):
    exception = InsufficientBalance(
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

    storage.has.return_value = False
    investment_planner.make_investment_plan.side_effect = exception
    message, result = investment_use_case.execute(basket)

    assert message == exception.message
    assert result is None

    investment_planner.make_investment_plan.assert_called_once_with(basket)
    exchange.execute_investment_plan.assert_not_called()
    storage.set.assert_not_called()


def test_invest_use_case_execute_already_invested(
    investment_use_case: BasketInvestUseCase,
    storage: Storage[BasketInvestment],
    basket: Basket,
):
    storage.has.return_value = True

    with raises(BasketAlreadyInvested):
        investment_use_case.execute(basket)
