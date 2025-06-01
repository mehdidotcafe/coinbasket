from decimal import Decimal
from unittest import mock
from invest_agent.investment.exception.no_basket_investment import NoBasketInvestment
from pytest import fixture, raises

from protocol.token import Token
from invest_agent.chain.balance import Balance
from invest_agent.investment.get_basket_investment_use_case import (
    GetBasketInvestmentUseCase,
)
from invest_agent.investment.basket_investment import (
    BasketInvestment,
    Bid,
)
from invest_agent.storage.storage import Storage


@fixture
def storage():
    return mock.Mock(spec=Storage[BasketInvestment])


def test_get_basket_investment_use_case(storage: Storage[BasketInvestment]):
    basket_investment = BasketInvestment(
        name="Test Basket",
        description="A test basket",
        invested_at="2020-05-09",
        type="basket investment",
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
                        name="Test Token",
                        display_name="Test",
                        ticker="TTK",
                        address="0x123",
                    ),
                ),
                buy_balance=Balance(
                    amount=Decimal("200"),
                    token=Token(
                        name="Test Token",
                        display_name="Test",
                        ticker="TTK",
                        address="0x123",
                    ),
                ),
            )
        ],
        status="invested",
    )
    storage.get.return_value = [basket_investment, 1]

    use_case = GetBasketInvestmentUseCase(storage)

    result = use_case.execute()

    assert result == basket_investment
    storage.get.assert_called_once_with("basket_investment")


def test_get_basket_investment_use_case_no_result(storage: Storage[BasketInvestment]):
    storage.get.return_value = None

    use_case = GetBasketInvestmentUseCase(storage)

    with raises(NoBasketInvestment):
        use_case.execute()

    storage.get.assert_called_once_with("basket_investment")
