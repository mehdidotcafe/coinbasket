from unittest import mock
from pytest import fixture
from decimal import Decimal
from web3 import Web3
from web3.eth import Eth

from coinbasket.basket import Token
from coinbasket.infrastructure.bsc.chain.bsc_chain import BscChain


@fixture
def w3():
    w3 = mock.Mock(spec=Web3)

    w3.eth = mock.Mock(spec=Eth)

    return w3


@fixture
def base_token():
    return Token(name="BNB", display_name="BNB", ticker="BNB", address="0x123456789")


@fixture
def bsc_chain(base_token: Token, w3: Web3):
    return BscChain(
        w3=w3,
        private_key="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        base_token=base_token,
    )


def test_get_min_balance(bsc_chain: BscChain, base_token: Token):
    min_balance = bsc_chain.get_min_balance()

    assert min_balance.amount == Decimal("1")
    assert min_balance.token == base_token
