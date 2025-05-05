from decimal import Decimal
from unittest import mock
from pytest import fixture

from invest_agent.basket import Token
from invest_agent.chain.balance import Balance
from invest_agent.investment.get_investment_result_use_case import (
    GetInvestmentResultUseCase,
)
from invest_agent.investment.investment_result import (
    InvestmentResult,
    InvestmentResultBid,
)
from invest_agent.storage.storage import Storage


@fixture
def storage():
    return mock.Mock(spec=Storage[InvestmentResult])


def test_get_investment_result_use_case(storage: Storage[InvestmentResult]):
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
                        name="Test Token",
                        display_name="Test",
                        ticker="TTK",
                        address="0x123",
                    ),
                ),
                balance_out=Balance(
                    amount=Decimal("200"),
                    token=Token(
                        name="Test Token",
                        display_name="Test",
                        ticker="TTK",
                        address="0x123",
                    ),
                ),
            )
        ]
    )
    storage.get.return_value = investment_result

    use_case = GetInvestmentResultUseCase(storage)

    result = use_case.execute()

    assert result == investment_result
    storage.get.assert_called_once_with("investment_result")


def test_get_investment_result_use_case_no_result(storage: Storage[InvestmentResult]):
    storage.get.return_value = None

    use_case = GetInvestmentResultUseCase(storage)

    result = use_case.execute()

    assert result == "No invested basket found."
    storage.get.assert_called_once_with("investment_result")
