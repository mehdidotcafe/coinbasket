from decimal import Decimal
from unittest import mock
from api.investment.confirmed_order import ConfirmedOrder
from api.investment.exchange.exchange import (
    Exchange,
    ExchangeSignableSwap,
    SignableTransaction,
)

from api.investment.signable_order import SignableOrder
from pytest import fixture

from api.chain.balance import Balance, BalanceAtomic
from api.protocol.fixture.token import wbnb_token, usdt_token

from api.investment.build_signable_order_use_case import (
    BuildSignableOrderUseCase,
)


@fixture
def exchange():
    return mock.Mock(spec=Exchange)


@fixture
def use_case(exchange: Exchange):
    return BuildSignableOrderUseCase(exchange=exchange)


async def test_build_signable_order_use_case_execute_success(
    exchange: Exchange,
    use_case: BuildSignableOrderUseCase,
):
    signed_swap = ExchangeSignableSwap(
        buy_balance=BalanceAtomic(
            asset=wbnb_token, amount=Decimal(0.5), amount_atomic=5 * 10**17, decimals=18
        ),
        sell_balance=BalanceAtomic(
            asset=usdt_token,
            amount=Decimal(150),
            amount_atomic=150 * 10**18,
            decimals=18,
        ),
        signature_payload={"some": "payload"},
        transaction=SignableTransaction(
            type="SEND",
            amount=200,
            data=b"0x5678",
            to_address="0x1234",
            gas=None,
        ),
    )
    exchange.get_signable_swap.return_value = signed_swap

    order = ConfirmedOrder(
        buy_balance=Balance(asset=wbnb_token, amount=Decimal(1)),
        sell_balance=Balance(asset=usdt_token, amount=Decimal(300)),
    )

    result = await use_case.execute(order)
    assert result == SignableOrder(
        buy_balance=signed_swap.buy_balance,
        sell_balance=signed_swap.sell_balance,
        signature_payload=signed_swap.signature_payload,
        transaction=signed_swap.transaction,
    )
