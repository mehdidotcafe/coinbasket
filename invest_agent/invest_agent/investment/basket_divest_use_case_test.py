from decimal import Decimal
from unittest import mock
from invest_agent.datetime.date_time import DateTime
from invest_agent.investment.basket_investment import BasketInvestment, Bid
from invest_agent.investment.exception.no_basket_investment import NoBasketInvestment
from invest_agent.investment.investment_parameters import InvestmentParameters
from pytest import fixture, raises

from protocol.token import Token
from invest_agent.chain.balance import Balance
from invest_agent.investment.basket_divest_use_case import BasketDivestUseCase
from invest_agent.investment.divestment_planner import DivestmentPlanner
from invest_agent.investment.exchange.exchange import Exchange
from invest_agent.investment.investment_plan import InvestmentPlan, InvestmentPlanStep
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


@fixture
def date_time():
    return mock.Mock(spec=DateTime)


def test_basket_divest_use_case_execute_no_investment(
    divestment_planner: DivestmentPlanner,
    exchange: Exchange,
    storage: Storage[BasketInvestment],
    date_time: DateTime,
):
    storage.get.return_value = None

    use_case = BasketDivestUseCase(divestment_planner, exchange, storage, date_time)

    with raises(NoBasketInvestment):
        use_case.execute()

    storage.get.assert_called_once_with("basket_investment")


def test_basket_divest_use_case_execute_exception(
    divestment_planner: DivestmentPlanner,
    exchange: Exchange,
    storage: Storage[BasketInvestment],
    date_time: DateTime,
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
    basket_investment = BasketInvestment(
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
                sell_balance=Balance(
                    amount=Decimal("100"),
                    token=Token(
                        name="Test Token 1",
                        display_name="Test 1",
                        ticker="TTK1",
                        address="0x1",
                    ),
                ),
                buy_balance=Balance(
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
    storage.get.return_value = [basket_investment, 1]
    divestment_planner.make_divestment_plan.return_value = divestment_plan

    exchange.execute_divestment_plan.side_effect = Exception("Error")

    use_case = BasketDivestUseCase(divestment_planner, exchange, storage, date_time)

    message, result = use_case.execute()

    assert message == "Divestment error: Error"
    assert result is None


def test_basket_divest_use_case_execute_success(
    divestment_planner: DivestmentPlanner,
    exchange: Exchange,
    storage: Storage[BasketInvestment],
    date_time: DateTime,
):
    basket_investment = BasketInvestment(
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
                sell_balance=Balance(
                    amount=Decimal("100"),
                    token=Token(
                        name="Test Token 1",
                        display_name="Test 1",
                        ticker="TTK1",
                        address="0x1",
                    ),
                ),
                buy_balance=Balance(
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
    basket_divestment = BasketInvestment(
        name="Test Basket",
        description="A test basket",
        invested_at="2020-05-09",
        type="basket divestment",
        bids=[
            Bid(
                token=Token(
                    name="WBNB",
                    display_name="WBNB",
                    ticker="WBNB",
                    address="0x238928933434",
                ),
                sell_balance=Balance(
                    amount=Decimal("200"),
                    token=Token(
                        name="Test Token",
                        display_name="Test",
                        ticker="TTK",
                        address="0x123",
                    ),
                ),
                buy_balance=Balance(
                    amount=Decimal("100"),
                    token=Token(
                        name="WBNB",
                        display_name="WBNB",
                        ticker="WBNB",
                        address="0x238928933434",
                    ),
                ),
            )
        ],
        status="invested",
    )

    storage.get.return_value = [basket_investment, 1]
    divestment_planner.make_divestment_plan.return_value = divestment_plan
    exchange.execute_divestment_plan.return_value = basket_divestment.bids
    date_time.now_str.return_value = "2020-05-09"

    use_case = BasketDivestUseCase(divestment_planner, exchange, storage, date_time)

    message, result = use_case.execute()

    assert message == "Divestment success."
    assert result == basket_divestment

    storage.get.assert_called_once_with("basket_investment")
    divestment_planner.make_divestment_plan.assert_called_once_with(basket_investment)
    exchange.execute_divestment_plan.assert_called_once_with(
        divestment_plan,
        InvestmentParameters(slippage_tolerance_in_percentage=Decimal("1")),
    )
    storage.remove.assert_called_once_with("basket_investment")
    date_time.now_str.assert_called_once()
