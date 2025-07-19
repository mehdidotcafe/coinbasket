from unittest import mock
from eth_typing import HexStr
from invest_agent.chain.chain import Gas
from invest_agent.chain.exception.insufficient_balance import InsufficientBalance
from invest_agent.infrastructure.bsc.chain.nonce_manager import NonceManager
from pytest import fixture, mark, raises
from decimal import Decimal
from web3 import AsyncWeb3
from web3.types import Wei
from web3.eth import AsyncEth


from protocol.token import Token
from protocol.fixture.token import eth_token
from invest_agent.infrastructure.bsc.chain.bsc_chain import BscChain

from eth_account.signers.local import LocalAccount

from protocol.fixture.token import bnb_token


@fixture
def w3():
    w3 = mock.Mock(spec=AsyncWeb3)

    w3.eth = mock.Mock(spec=AsyncEth)

    account = mock.Mock(spec=LocalAccount)
    account.address = "0x1234567890abcdef1234567890abcdef12345678"

    w3.to_checksum_address.side_effect = lambda x: f"{x}_checksum"
    w3.eth._gas_price = mock.AsyncMock(return_value=Wei(1_000_000_000))
    w3.eth.account.from_key.return_value = account
    w3.eth._chain_id = mock.AsyncMock(return_value=42)

    return w3


@fixture
def base_token():
    return bnb_token


@fixture
def nonce_manager():
    nonce_manager = mock.Mock(spec=NonceManager)
    nonce_manager.get_and_increment = mock.AsyncMock(return_value=9)
    return nonce_manager


@fixture
def bsc_chain(w3: AsyncWeb3, nonce_manager: NonceManager):
    return BscChain(
        w3=w3,
        private_key="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        nonce_manager=nonce_manager,
    )


def test_bsc_chain_is_native_token_success(bsc_chain: BscChain, base_token: Token):
    assert bsc_chain.is_native_token(base_token) is True


def test_bsc_chain_is_native_token_failure(bsc_chain: BscChain):
    assert bsc_chain.is_native_token(eth_token) is False


@mark.asyncio
async def test_bsc_chain_get_chain_id_with_cache(bsc_chain: BscChain):
    chain_id = await bsc_chain.get_chain_id()

    assert chain_id == 42

    bsc_chain.w3.eth._chain_id.assert_called_once()

    chain_id_cached = await bsc_chain.get_chain_id()

    assert chain_id_cached == 42

    # Ensure the cached value is used on subsequent calls
    bsc_chain.w3.eth._chain_id.assert_called_once()


def test_bsc_chain_get_address(bsc_chain: BscChain):
    address = bsc_chain.get_address()

    assert address == "0x1234567890abcdef1234567890abcdef12345678"

    bsc_chain.w3.eth.account.from_key.assert_called_once_with(
        "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    )


@mark.asyncio
async def test_bsc_chain_get_min_balance(
    bsc_chain: BscChain, base_token: Token, w3: AsyncWeb3
):
    w3.from_wei.return_value = Decimal("1")

    min_balance = await bsc_chain.get_min_balance()

    assert min_balance.amount == Decimal("1")
    assert min_balance.token == base_token

    w3.from_wei.assert_called_once_with(
        1_000_000_000 * 200_000 * 20,
        "ether",
    )


@mark.asyncio
async def test_bsc_chain_get_balance(
    bsc_chain: BscChain, w3: AsyncWeb3, base_token: Token
):
    w3.eth.get_balance.return_value = Wei(1000000000000000000)
    w3.from_wei.return_value = Decimal("1")

    balance = await bsc_chain.get_balance()

    assert balance.amount == Decimal("1")
    assert balance.token == base_token

    w3.eth.get_balance.assert_called_once_with(
        "0x1234567890abcdef1234567890abcdef12345678",
    )
    w3.from_wei.assert_called_once_with(
        Wei(1000000000000000000),
        "ether",
    )


@mark.asyncio
async def test_bsc_chain_get_available_balance_insufficient_balance(
    bsc_chain: BscChain, w3: AsyncWeb3
):
    w3.eth.get_balance.return_value = Wei(100)
    w3.from_wei.side_effect = lambda x, _unit: x

    with raises(InsufficientBalance):
        await bsc_chain.get_available_balance()


@mark.asyncio
async def test_bsc_chain_get_available_balance(
    bsc_chain: BscChain, w3: AsyncWeb3, base_token: Token
):
    w3.eth.get_balance.return_value = Wei(1000000000000000000)
    w3.from_wei.side_effect = lambda x, _unit: x

    balance = await bsc_chain.get_available_balance()

    assert balance.amount == Decimal(
        1000000000000000000 - (1_000_000_000 * 200_000 * 20)
    )
    assert balance.token == base_token

    w3.eth.get_balance.assert_called_once_with(
        "0x1234567890abcdef1234567890abcdef12345678",
    )


@mark.asyncio
async def test_bsc_chain_get_token_balance_amount(bsc_chain: BscChain, w3: AsyncWeb3):
    token_address = "0xabcdefabcdefabcdefabcdefabcdefabcdefabcdef"

    token_contract = mock.Mock()
    token_contract.functions.balanceOf.return_value.call = mock.AsyncMock(
        return_value=1000
    )
    w3.eth.contract.return_value = token_contract

    w3.from_wei.return_value = Decimal("1")

    balance = await bsc_chain.get_token_balance_amount(token_address)

    assert balance == Decimal("1")

    token_contract.functions.balanceOf.assert_called_once_with(
        "0x1234567890abcdef1234567890abcdef12345678",
    )
    token_contract.functions.balanceOf.return_value.call.assert_called_once()


@mark.asyncio
async def test_bsc_chain_get_address_balance(
    bsc_chain: BscChain, w3: AsyncWeb3, base_token: Token
):
    address = "0x2B5616d51Cd04862a6BD16cE63B47364A2261125"

    w3.eth.get_balance.return_value = Wei(1000000000000000000)
    w3.from_wei.return_value = Decimal("1")

    balance = await bsc_chain.get_address_balance(address)

    assert balance.amount == Decimal("1")
    assert balance.token == base_token

    w3.eth.get_balance.assert_called_once_with(
        "0x2B5616d51Cd04862a6BD16cE63B47364A2261125_checksum",
    )
    w3.from_wei.assert_called_once_with(
        Wei(1000000000000000000),
        "ether",
    )


@mark.asyncio
async def test_bsc_chain_get_address_token_balance_amount(
    bsc_chain: BscChain, w3: AsyncWeb3
):
    address = "0x2B5616d51Cd04862a6BD16cE63B47364A2261125"
    token_address = "0xabcdefabcdefabcdefabcdefabcdefabcdefabcdef"

    token_contract = mock.Mock()
    token_contract.functions.balanceOf.return_value.call = mock.AsyncMock(
        return_value=1000
    )
    w3.eth.contract.return_value = token_contract

    w3.from_wei.return_value = Decimal("1")

    balance = await bsc_chain.get_address_token_balance_amount(address, token_address)

    assert balance == Decimal("1")

    token_contract.functions.balanceOf.assert_called_once_with(
        "0x2B5616d51Cd04862a6BD16cE63B47364A2261125_checksum",
    )
    token_contract.functions.balanceOf.return_value.call.assert_called_once()


def test_bsc_chain_get_base_token(bsc_chain: BscChain, base_token: Token):
    base_token_result = bsc_chain.get_base_token()

    assert base_token_result == base_token


@mark.asyncio
async def test_bsc_chain_compute_gas_estimate(bsc_chain: BscChain, w3: AsyncWeb3):
    amount = 1000
    to_address = "0xabcdefabcdefabcdefabcdefabcdefabcdefabcdef"
    encoded_input = HexStr("0x1234567890abcdef")
    gas = int(21000 * 1.1)

    w3.eth.estimate_gas.return_value = 21000

    gas_estimate = await bsc_chain.compute_gas_estimate(
        amount, to_address, encoded_input
    )

    assert gas_estimate == gas

    w3.eth.estimate_gas.assert_called_once_with(
        {
            "from": "0x1234567890abcdef1234567890abcdef12345678",
            "to": to_address,
            "value": amount,
            "data": encoded_input,
        }
    )


@mark.asyncio
async def test_bsc_chain_compute_gas_estimate_without_encoded_input(
    bsc_chain: BscChain, w3: AsyncWeb3
):
    amount = 1000
    to_address = "0xabcdefabcdefabcdefabcdefabcdefabcdefabcdef"

    w3.eth.estimate_gas.return_value = 21000

    await bsc_chain.compute_gas_estimate(amount, to_address)

    w3.eth.estimate_gas.assert_called_once_with(
        {
            "from": "0x1234567890abcdef1234567890abcdef12345678",
            "to": to_address,
            "value": amount,
        }
    )


@mark.asyncio
async def test_bsc_chain_sign_send_transaction_without_gas_params(
    bsc_chain: BscChain, w3: AsyncWeb3
):
    amount = 1000
    encoded_input = HexStr("0xbadf00d")

    w3.eth.send_transaction.return_value = "0xtransactionhash"
    block_data = mock.Mock()
    block_data.get.return_value = Wei(1_000_000_000)

    w3.eth.get_block = mock.AsyncMock(return_value=block_data)
    w3.to_wei.return_value = Wei(5_000_000)

    await bsc_chain.sign_send_transaction(
        amount=amount,
        encoded_input=encoded_input,
        to_address="0xabcdefabcdefabcdefabcdefabcdefabcdefabcdef",
    )

    w3.eth.send_transaction.assert_called_once_with(
        {
            "from": mock.ANY,
            "chainId": mock.ANY,
            "value": mock.ANY,
            "nonce": mock.ANY,
            "data": mock.ANY,
            "type": 2,
            "maxFeePerGas": Wei(2_005_000_000),
            "maxPriorityFeePerGas": Wei(5_000_000),
            "to": mock.ANY,
        }
    )


@mark.asyncio
async def test_bsc_chain_sign_send_transaction_success(
    bsc_chain: BscChain, w3: AsyncWeb3
):
    amount = 1000
    gas = Gas(gas=21000, gas_price=1_000_000_000)
    encoded_input = HexStr("0xbadf00d")

    w3.eth.send_transaction.return_value = "0xtransactionhash"

    transaction_hash = await bsc_chain.sign_send_transaction(
        amount=amount,
        gas=gas,
        encoded_input=encoded_input,
        to_address="0xabcdefabcdefabcdefabcdefabcdefabcdefabcdef",
    )

    w3.eth.send_transaction.assert_called_once_with(
        {
            "from": "0x1234567890abcdef1234567890abcdef12345678",
            "chainId": 42,
            "value": Wei(1000),
            "nonce": 9,
            "data": HexStr("0xbadf00d"),
            "gas": 21000,
            "gasPrice": Wei(1_000_000_000),
            "to": "0xabcdefabcdefabcdefabcdefabcdefabcdefabcdef_checksum",
        }
    )

    assert transaction_hash == "0xtransactionhash"


@mark.asyncio
async def test_bsc_chain_wait_transaction_success(bsc_chain: BscChain, w3: AsyncWeb3):
    transaction_hash = "0xtransactionhash"

    w3.eth.wait_for_transaction_receipt.return_value = {
        "status": 1,
        "blockNumber": 123456,
    }

    is_success = await bsc_chain.wait_transaction(transaction_hash)

    w3.eth.wait_for_transaction_receipt.assert_called_once_with(
        HexStr(transaction_hash)
    )

    assert is_success


@mark.asyncio
async def test_bsc_chain_wait_transaction_failure(bsc_chain: BscChain, w3: AsyncWeb3):
    transaction_hash = "0xtransactionhash"

    w3.eth.wait_for_transaction_receipt.return_value = {
        "status": 0,
        "blockNumber": 123456,
    }

    is_success = await bsc_chain.wait_transaction(transaction_hash)

    w3.eth.wait_for_transaction_receipt.assert_called_once_with(
        HexStr(transaction_hash)
    )

    assert not is_success
