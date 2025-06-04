from decimal import Decimal
from unittest import mock
from invest_agent.chain.chain import Chain
from invest_agent.datetime.date_time import DateTime
from invest_agent.investment.basket_investment import BasketInvestment, Bid
from invest_agent.investment.exception.no_basket_investment import NoBasketInvestment
from invest_agent.investment.investment_parameters import (
    IntegratorFee,
    InvestmentParameters,
)
from pytest import fixture, raises

from protocol.token import Token
from protocol.fixture.token import bnb_token
from invest_agent.chain.balance import Balance
from invest_agent.investment.basket_divest_use_case import (
    BasketDivestUseCase,
    Configuration,
)
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


@fixture
def chain():
    return mock.Mock(spec=Chain)


@fixture
def configuration() -> Configuration:
    return {
        "fee_integrator_address": "0x1234567890abcdef1234567890abcdef12345678",
        "fee_value_in_percentage": Decimal(0.15),
    }


@fixture
def basket_investment():
    return BasketInvestment(
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


@fixture
def divestment_plan():
    return InvestmentPlan(
        steps=[
            InvestmentPlanStep(
                token=Token(
                    name="Test Token 1",
                    display_name="Test 1",
                    ticker="TTK1",
                    address="0x1",
                ),
                sell_balance=Balance(
                    amount=Decimal("100"),
                    token=Token(
                        name="Test Token",
                        display_name="Test",
                        ticker="TTK",
                        address="0x123",
                    ),
                ),
            ),
            InvestmentPlanStep(
                token=Token(
                    name="Test Token 2",
                    display_name="Test 2",
                    ticker="TTK2",
                    address="0x2",
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
            ),
        ],
        sell_total_balance=Balance(
            amount=Decimal("0"),
            token=Token(
                name="Test Token",
                display_name="Test",
                ticker="TTK",
                address="0x123",
            ),
        ),
    )


@fixture
def basket_divestment():
    return BasketInvestment(
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


def test_basket_divest_use_case_execute_no_investment(
    divestment_planner: DivestmentPlanner,
    exchange: Exchange,
    storage: Storage[BasketInvestment],
    date_time: DateTime,
    chain: Chain,
    configuration: Configuration,
):
    storage.get.return_value = None

    use_case = BasketDivestUseCase(
        divestment_planner=divestment_planner,
        exchange=exchange,
        storage=storage,
        date_time=date_time,
        chain=chain,
        configuration=configuration,
    )

    with raises(NoBasketInvestment):
        use_case.execute()

    storage.get.assert_called_once_with("basket_investment")


def test_basket_divest_use_case_execute_exception(
    divestment_planner: DivestmentPlanner,
    exchange: Exchange,
    storage: Storage[BasketInvestment],
    date_time: DateTime,
    chain: Chain,
    configuration: Configuration,
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
                sell_balance=Balance(
                    token=Token(
                        name="Test Token",
                        display_name="Test",
                        ticker="TTK",
                        address="0x123",
                    ),
                    amount=Decimal("100"),
                ),
            ),
            InvestmentPlanStep(
                token=Token(
                    name="Test Token 2",
                    display_name="Test 2",
                    ticker="TTK2",
                    address="0x2",
                ),
                sell_balance=Balance(
                    token=Token(
                        name="Test Token",
                        display_name="Test",
                        ticker="TTK",
                        address="0x123",
                    ),
                    amount=Decimal("200"),
                ),
            ),
        ],
        sell_total_balance=Balance(
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

    use_case = BasketDivestUseCase(
        divestment_planner=divestment_planner,
        exchange=exchange,
        storage=storage,
        date_time=date_time,
        chain=chain,
        configuration=configuration,
    )

    message, result = use_case.execute()

    assert message == "Divestment error: Error"
    assert result is None


def test_basket_divest_use_case_execute_success(
    divestment_planner: DivestmentPlanner,
    exchange: Exchange,
    storage: Storage[BasketInvestment],
    date_time: DateTime,
    chain: Chain,
    configuration: Configuration,
    basket_investment: BasketInvestment,
    divestment_plan: InvestmentPlan,
    basket_divestment: BasketInvestment,
):
    storage.get.return_value = [basket_investment, 1]
    chain.get_base_token.return_value = bnb_token
    divestment_planner.make_divestment_plan.return_value = divestment_plan
    exchange.execute_divestment_plan.return_value = basket_divestment.bids
    date_time.now_str.return_value = "2020-05-09"

    use_case = BasketDivestUseCase(
        divestment_planner=divestment_planner,
        exchange=exchange,
        storage=storage,
        date_time=date_time,
        chain=chain,
        configuration=configuration,
    )

    message, result = use_case.execute()

    assert message == "Divestment success."
    assert result == basket_divestment

    storage.get.assert_called_once_with("basket_investment")
    divestment_planner.make_divestment_plan.assert_called_once_with(basket_investment)
    exchange.execute_divestment_plan.assert_called_once_with(
        divestment_plan,
        InvestmentParameters(
            slippage_tolerance_in_percentage=Decimal("1"),
            integrator_fee=IntegratorFee(
                recipient="0x1234567890abcdef1234567890abcdef12345678",
                value_in_percentage=Decimal(0.15),
                token=bnb_token,
            ),
        ),
    )
    storage.remove.assert_called_once_with("basket_investment")
    date_time.now_str.assert_called_once()


def test_basket_divest_use_case_execute_with_no_integrator_fee(
    divestment_planner: DivestmentPlanner,
    exchange: Exchange,
    storage: Storage[BasketInvestment],
    date_time: DateTime,
    chain: Chain,
    basket_investment: BasketInvestment,
    divestment_plan: InvestmentPlan,
    basket_divestment: BasketInvestment,
):
    storage.get.return_value = [basket_investment, 1]
    divestment_planner.make_divestment_plan.return_value = divestment_plan
    exchange.execute_divestment_plan.return_value = basket_divestment.bids
    date_time.now_str.return_value = "2020-05-09"

    use_case = BasketDivestUseCase(
        divestment_planner=divestment_planner,
        exchange=exchange,
        storage=storage,
        date_time=date_time,
        chain=chain,
        configuration=Configuration(
            fee_integrator_address=None,
            fee_value_in_percentage=None,
        ),
    )

    use_case.execute()

    exchange.execute_divestment_plan.assert_called_once_with(
        mock.ANY,
        InvestmentParameters(
            slippage_tolerance_in_percentage=mock.ANY,
            integrator_fee=None,
        ),
    )
