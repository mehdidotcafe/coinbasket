from unittest import mock
from eth_typing import HexStr
from pytest import fixture
from decimal import Decimal
from web3 import Web3
from web3.types import Wei
from web3.eth import Eth
from eth_account.signers.local import LocalAccount

from invest_agent.basket import Token
from invest_agent.infrastructure.bsc.chain.bsc_chain import BscChain


@fixture
def w3():
    w3 = mock.Mock(spec=Web3)

    w3.eth = mock.Mock(spec=Eth)

    account = mock.Mock(spec=LocalAccount)
    account.address = "0x1234567890abcdef1234567890abcdef12345678"

    w3.eth.gas_price = Wei(1_000_000_000)
    w3.eth.account.from_key.return_value = account

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


def test_get_min_balance(bsc_chain: BscChain, base_token: Token, w3: Web3):
    w3.from_wei.return_value = Decimal("1")

    min_balance = bsc_chain.get_min_balance()

    assert min_balance.amount == Decimal("1")
    assert min_balance.token == base_token

    w3.from_wei.assert_called_once_with(
        1_000_000_000 * 200_000 * 20,
        "ether",
    )


def test_get_balance(bsc_chain: BscChain, w3: Web3, base_token: Token):
    w3.eth.get_balance.return_value = Wei(1000000000000000000)
    w3.from_wei.return_value = Decimal("1")

    balance = bsc_chain.get_balance()

    assert balance.amount == Decimal("1")
    assert balance.token == base_token

    w3.eth.get_balance.assert_called_once_with(
        "0x1234567890abcdef1234567890abcdef12345678",
    )
    w3.from_wei.assert_called_once_with(
        Wei(1000000000000000000),
        "ether",
    )


def test_get_token_balance_amount(bsc_chain: BscChain, w3: Web3):
    token_address = "0xabcdefabcdefabcdefabcdefabcdefabcdefabcdef"

    token_contract = mock.Mock()
    token_contract.functions.balanceOf.return_value.call.return_value = 1000
    w3.eth.contract.return_value = token_contract

    w3.from_wei.return_value = Decimal("1")

    balance = bsc_chain.get_token_balance_amount(token_address)

    assert balance == Decimal("1")

    token_contract.functions.balanceOf.assert_called_once_with(
        "0x1234567890abcdef1234567890abcdef12345678",
    )
    token_contract.functions.balanceOf.return_value.call.assert_called_once()


def test_get_base_token(bsc_chain: BscChain, base_token: Token):
    base_token_result = bsc_chain.get_base_token()

    assert base_token_result == base_token


def test_compute_gas_estimate(bsc_chain: BscChain, w3: Web3):
    amount = 1000
    to_address = "0xabcdefabcdefabcdefabcdefabcdefabcdefabcdef"
    encoded_input = HexStr("0x1234567890abcdef")
    gas = int(21000 * 1.1)

    w3.eth.estimate_gas.return_value = 21000

    gas_estimate = bsc_chain.compute_gas_estimate(amount, to_address, encoded_input)

    assert gas_estimate == gas

    w3.eth.estimate_gas.assert_called_once_with(
        {
            "from": "0x1234567890abcdef1234567890abcdef12345678",
            "to": to_address,
            "value": amount,
            "data": encoded_input,
        }
    )


def test_compute_gas_estimate_without_encoded_input(bsc_chain: BscChain, w3: Web3):
    amount = 1000
    to_address = "0xabcdefabcdefabcdefabcdefabcdefabcdefabcdef"

    w3.eth.estimate_gas.return_value = 21000

    bsc_chain.compute_gas_estimate(amount, to_address)

    w3.eth.estimate_gas.assert_called_once_with(
        {
            "from": "0x1234567890abcdef1234567890abcdef12345678",
            "to": to_address,
            "value": amount,
        }
    )
