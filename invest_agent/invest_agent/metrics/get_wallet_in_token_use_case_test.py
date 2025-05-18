from decimal import Decimal
from unittest import mock
from invest_agent.chain.balance import Balance
from invest_agent.chain.chain import Chain
from invest_agent.investment.basket_investment import BasketInvestment, Bid
from invest_agent.investment.exchange.exchange import Wallet, Exchange
from invest_agent.metrics.exception.basket_investment_not_found_exception import (
    BasketInvestmentNotFoundException,
)
from invest_agent.metrics.get_wallet_in_token_use_case import (
    GetWalletInTokenUseCase,
)
from invest_agent.storage.storage import Storage
from protocol.token import Token
from pytest import fixture, raises


@fixture
def storage():
    return mock.Mock(spec=Storage[BasketInvestment])


@fixture
def exchange():
    return mock.Mock(spec=Exchange)


@fixture
def chain():
    return mock.Mock(spec=Chain)


@fixture
def basket_investment():
    return BasketInvestment(
        name="basket_investment",
        description="description",
        type="type",
        invested_at="2023-10-01T00:00:00Z",
        bids=[
            Bid(
                token=Token(
                    name="Token 1",
                    display_name="Token 1",
                    ticker="TK1",
                    address="0x00001",
                ),
                balance_in=Balance(
                    amount=Decimal("1000"),
                    token=Token(
                        name="Token 1",
                        display_name="Token 1",
                        ticker="TK1",
                        address="0x00001",
                    ),
                ),
                balance_out=Balance(
                    amount=Decimal("333"),
                    token=Token(
                        name="Token 8",
                        display_name="Token 8",
                        ticker="TK8",
                        address="0x00008",
                    ),
                ),
            ),
            Bid(
                token=Token(
                    name="Token 2",
                    display_name="Token 2",
                    ticker="TK2",
                    address="0x00002",
                ),
                balance_in=Balance(
                    amount=Decimal("99999"),
                    token=Token(
                        name="Token 2",
                        display_name="Token 2",
                        ticker="TK2",
                        address="0x00002",
                    ),
                ),
                balance_out=Balance(
                    amount=Decimal("9384"),
                    token=Token(
                        name="Token 9",
                        display_name="Token 9",
                        ticker="TK9",
                        address="0x00009",
                    ),
                ),
            ),
        ],
    )


def test_get_wallet_in_token_use_case_basket_investment_not_found(
    storage: Storage[BasketInvestment], exchange: Exchange, chain: Chain
):
    storage.get.return_value = None
    chain.get_balance.return_value = Balance(
        amount=Decimal("0"),
        token=Token(
            name="BNB",
            display_name="BNB",
            ticker="BNB",
            address="0x00000",
        ),
    )

    use_case = GetWalletInTokenUseCase(storage, exchange, chain)

    use_case.execute(
        Token(
            name="Tether USD",
            display_name="Tether USD",
            ticker="USDT",
            address="0x55d398326f99059ff775485246999027b3197955",
        ),
    )

    exchange.get_wallet_in_token.assert_called_once_with(
        [
            Balance(
                amount=Decimal("0"),
                token=Token(
                    name="BNB",
                    display_name="BNB",
                    ticker="BNB",
                    address="0x00000",
                ),
            ),
        ],
        mock.ANY,
    )


def test_get_wallet_in_token_use_case_basket_investment(
    storage: Storage[BasketInvestment],
    exchange: Exchange,
    basket_investment: BasketInvestment,
    chain: Chain,
):
    storage.get.return_value = [basket_investment, 1]
    chain.get_balance.return_value = Balance(
        amount=Decimal("0"),
        token=Token(
            name="BNB",
            display_name="BNB",
            ticker="BNB",
            address="0x00000",
        ),
    )
    exchange.get_wallet_in_token.return_value = Wallet(
        balances=[],
        total_balance=Balance(
            amount=Decimal("0"),
            token=Token(
                name="Tether USD",
                display_name="Tether USD",
                ticker="USDT",
                address="0x55d398326f99059ff775485246999027b3197955",
            ),
        ),
    )

    use_case = GetWalletInTokenUseCase(storage, exchange, chain)

    result = use_case.execute(
        Token(
            name="Tether USD",
            display_name="Tether USD",
            ticker="USDT",
            address="0x55d398326f99059ff775485246999027b3197955",
        ),
    )

    assert result == Wallet(
        balances=[],
        total_balance=Balance(
            amount=Decimal("0"),
            token=Token(
                name="Tether USD",
                display_name="Tether USD",
                ticker="USDT",
                address="0x55d398326f99059ff775485246999027b3197955",
            ),
        ),
    )

    storage.get.assert_called_once_with("basket_investment")
    exchange.get_wallet_in_token.assert_called_once_with(
        [
            Balance(
                amount=Decimal("0"),
                token=Token(
                    name="BNB",
                    display_name="BNB",
                    ticker="BNB",
                    address="0x00000",
                ),
            ),
            Balance(
                amount=Decimal("333"),
                token=Token(
                    name="Token 8",
                    display_name="Token 8",
                    ticker="TK8",
                    address="0x00008",
                ),
            ),
            Balance(
                amount=Decimal("9384"),
                token=Token(
                    name="Token 9",
                    display_name="Token 9",
                    ticker="TK9",
                    address="0x00009",
                ),
            ),
        ],
        Token(
            name="Tether USD",
            display_name="Tether USD",
            ticker="USDT",
            address="0x55d398326f99059ff775485246999027b3197955",
        ),
    )
