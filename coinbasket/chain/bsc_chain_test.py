from pytest import fixture
from decimal import Decimal

from coinbasket.basket import Token
from coinbasket.chain.bsc_chain import BscChain


@fixture
def base_token():
    return Token(name="BNB", display_name="BNB", ticker="BNB", address="0x123456789")


@fixture
def bsc_chain(base_token: Token):
    return BscChain(
        rpc_url="https://bsc-dataseed.binance.org/",
        private_key="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        base_token=base_token,
    )


def test_defined(bsc_chain: BscChain):
    assert bsc_chain is not None


def test_get_min_balance(bsc_chain: BscChain, base_token: Token):
    min_balance = bsc_chain.get_min_balance()

    assert min_balance.amount == Decimal("1")
    assert min_balance.token == base_token
