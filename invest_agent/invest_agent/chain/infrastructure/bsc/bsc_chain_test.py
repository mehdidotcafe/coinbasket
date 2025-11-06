from typing import Any
from unittest import mock
from eth_typing import HexStr
from hexbytes import HexBytes
from invest_agent.chain.balance import AmountReadable, BalanceAtomic
from invest_agent.chain.chain import Gas, ParsedReceipt
from invest_agent.chain.exception.insufficient_balance import InsufficientBalance
from invest_agent.chain.infrastructure.bsc.nonce_manager import NonceManager
from invest_agent.chain.infrastructure.bsc.transaction_receipt_parser import (
    BscTransactionReceiptParser,
)
from pytest import fixture, mark, raises
from decimal import Decimal
from web3 import AsyncWeb3
from web3.types import Wei
from web3.eth import AsyncEth


from protocol.token import Token
from protocol.fixture.token import eth_token, usdt_token
from invest_agent.chain.infrastructure.bsc.bsc_chain import BscChain

from eth_account.signers.local import LocalAccount

from protocol.fixture.token import bnb_token, wbnb_token


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
def transaction_receipt_parser():
    return mock.Mock(spec=BscTransactionReceiptParser)


@fixture
def bsc_chain(
    w3: AsyncWeb3,
    nonce_manager: NonceManager,
    transaction_receipt_parser: BscTransactionReceiptParser,
):
    return BscChain(
        w3=w3,
        private_key="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        nonce_manager=nonce_manager,
        transaction_receipt_parser=transaction_receipt_parser,
    )


def test_bsc_chain_is_native_token_success(bsc_chain: BscChain, base_token: Token):
    assert bsc_chain.is_native_token(base_token) is True


def test_bsc_chain_is_native_token_failure(bsc_chain: BscChain):
    assert bsc_chain.is_native_token(eth_token) is False


def test_bsc_chain_is_wrapped_native_token_success(bsc_chain: BscChain):
    assert bsc_chain.is_wrapped_native_token(wbnb_token) is True


def test_bsc_chain_is_wrapped_native_token_failure(bsc_chain: BscChain):
    assert bsc_chain.is_wrapped_native_token(eth_token) is False


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
    assert min_balance.asset == base_token

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

    balance = await bsc_chain.get_native_token_balance()

    assert balance.amount == Decimal("1")
    assert balance.asset == base_token

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
        await bsc_chain.get_native_token_available_balance()


@mark.asyncio
async def test_bsc_chain_get_available_balance(
    bsc_chain: BscChain, w3: AsyncWeb3, base_token: Token
):
    w3.eth.get_balance.return_value = Wei(1000000000000000000)
    w3.from_wei.side_effect = lambda x, _unit: x

    balance = await bsc_chain.get_native_token_available_balance()

    assert balance.amount == Decimal(
        1000000000000000000 - (1_000_000_000 * 200_000 * 20)
    )
    assert balance.asset == base_token

    w3.eth.get_balance.assert_called_once_with(
        "0x1234567890abcdef1234567890abcdef12345678",
    )


@mark.asyncio
async def test_bsc_chain_get_token_balance(bsc_chain: BscChain, w3: AsyncWeb3):
    token = Token(
        id="bsc:0xabcdefabcdefabcdefabcdefabcdefabcdefabcdef",
        name="Fake token",
        display_name="Fake token",
        ticker="FTK",
        address="0xabcdefabcdefabcdefabcdefabcdefabcdefabcdef",
    )

    token_contract = mock.Mock()
    token_contract.functions.balanceOf.return_value.call = mock.AsyncMock(
        return_value=1000
    )
    token_contract.functions.decimals.return_value.call = mock.AsyncMock(return_value=3)
    w3.eth.contract.return_value = token_contract

    w3.from_wei.return_value = Decimal("1")

    balance = await bsc_chain.get_token_balance(token)

    assert balance == BalanceAtomic[Token](
        asset=token, amount=Decimal("1"), amount_atomic=1000, decimals=3
    )
    token_contract.functions.balanceOf.return_value.call.assert_called_once()
    token_contract.functions.decimals.return_value.call.assert_called_once()


@mark.asyncio
async def test_bsc_chain_get_address_balance(
    bsc_chain: BscChain, w3: AsyncWeb3, base_token: Token
):
    address = "0x2B5616d51Cd04862a6BD16cE63B47364A2261125"

    w3.eth.get_balance.return_value = Wei(1000000000000000000)
    w3.from_wei.return_value = Decimal("1")

    balance = await bsc_chain.get_address_native_token_balance(address)

    assert balance.amount == Decimal("1")
    assert balance.asset == base_token

    w3.eth.get_balance.assert_called_once_with(
        "0x2B5616d51Cd04862a6BD16cE63B47364A2261125_checksum",
    )
    w3.from_wei.assert_called_once_with(
        Wei(1000000000000000000),
        "ether",
    )


@mark.asyncio
async def test_bsc_chain_get_address_token_balance(bsc_chain: BscChain, w3: AsyncWeb3):
    address = "0x2B5616d51Cd04862a6BD16cE63B47364A2261125"
    token = Token(
        id="bsc:0xabcdefabcdefabcdefabcdefabcdefabcdefabcdef",
        name="Fake token",
        display_name="Fake token",
        ticker="FTK",
        address="0xabcdefabcdefabcdefabcdefabcdefabcdefabcdef",
    )

    token_contract = mock.Mock()
    token_contract.functions.balanceOf.return_value.call = mock.AsyncMock(
        return_value=1000
    )
    token_contract.functions.decimals.return_value.call = mock.AsyncMock(return_value=3)
    w3.eth.contract.return_value = token_contract

    balance = await bsc_chain.get_address_token_balance(address, token)

    assert balance == BalanceAtomic[Token](
        asset=token, amount=Decimal("1"), amount_atomic=1000, decimals=3
    )

    token_contract.functions.balanceOf.assert_called_once_with(
        "0x2B5616d51Cd04862a6BD16cE63B47364A2261125_checksum",
    )
    token_contract.functions.balanceOf.return_value.call.assert_called_once()
    token_contract.functions.decimals.return_value.call.assert_called_once()


def test_bsc_chain_get_base_token(bsc_chain: BscChain, base_token: Token):
    base_token_result = bsc_chain.get_base_token()

    assert base_token_result == base_token


def test_bsc_chain_get_wrapped_base_token(bsc_chain: BscChain):
    base_token_result = bsc_chain.get_wrapped_base_token()

    assert base_token_result == wbnb_token


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

    w3.eth.send_transaction = mock.AsyncMock(return_value=HexBytes("0x128938348"))
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

    w3.eth.send_transaction = mock.AsyncMock(return_value=HexBytes("0x0128938348"))

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

    assert transaction_hash == "0x0128938348"


@mark.asyncio
async def test_bsc_chain_wait_transaction_success(bsc_chain: BscChain, w3: AsyncWeb3):
    transaction_hash = "0x123994844"

    w3.eth.wait_for_transaction_receipt.return_value = {
        "status": 1,
        "blockNumber": 123456,
    }

    is_success = await bsc_chain.wait_transaction(transaction_hash)

    w3.eth.wait_for_transaction_receipt.assert_called_once_with(
        HexBytes("0x123994844"), timeout=1200
    )

    assert is_success


@mark.asyncio
async def test_bsc_chain_wait_transaction_failure(bsc_chain: BscChain, w3: AsyncWeb3):
    transaction_hash = "0x123994844"

    w3.eth.wait_for_transaction_receipt.return_value = {
        "status": 0,
        "blockNumber": 123456,
    }

    is_success = await bsc_chain.wait_transaction(transaction_hash)

    w3.eth.wait_for_transaction_receipt.assert_called_once_with(
        HexBytes("0x123994844"), timeout=1200
    )

    assert not is_success


@mark.asyncio
async def test_bsc_chain_wait_transaction_raise(bsc_chain: BscChain, w3: AsyncWeb3):
    transaction_hash = "0x123994844"

    w3.eth.wait_for_transaction_receipt.side_effect = Exception("Some error")
    is_success = await bsc_chain.wait_transaction(transaction_hash)

    assert not is_success


@mark.asyncio
async def test_bsc_chain_parse_transaction_receipt(
    bsc_chain: BscChain,
    w3: AsyncWeb3,
    transaction_receipt_parser: BscTransactionReceiptParser,
):
    transaction_hash = "0x123994844"
    sell_token = usdt_token
    buy_token = bnb_token
    parsed_receipt = ParsedReceipt(
        executed_sell_balance=BalanceAtomic(
            amount=Decimal("0.33"),
            amount_atomic=int(0.33 * 10**18),
            asset=bnb_token,
            decimals=18,
        ),
        executed_buy_balance=BalanceAtomic(
            amount=Decimal("5.12"),
            amount_atomic=512 * 10**16,
            asset=usdt_token,
            decimals=18,
        ),
    )
    receipt: dict[str, Any] = {
        "type": 0,
        "status": 1,
        "cumulativeGasUsed": 144955,
        "logs": [],
    }

    w3.eth.get_transaction_receipt.return_value = receipt

    transaction_receipt_parser.parse_receipt.return_value = parsed_receipt

    result = await bsc_chain.parse_transaction_receipt(
        sell_token=sell_token, buy_token=buy_token, transaction_hash=transaction_hash
    )

    transaction_receipt_parser.parse_receipt.assert_called_once_with(
        address="0x1234567890abcdef1234567890abcdef12345678",
        sell_token=sell_token,
        buy_token=buy_token,
        receipt=receipt,
    )

    assert result == parsed_receipt


@mark.asyncio
async def test_bsc_chain_convert_amount_to_amount_atomic_native_token(
    bsc_chain: BscChain, w3: AsyncWeb3
):
    amount_atomic = 1250000000000000000
    amount_readable = AmountReadable("1.25")

    token_contract = mock.Mock()
    w3.eth.contract.return_value = token_contract

    result_amount, result_decimals = await bsc_chain.convert_amount_to_amount_atomic(
        bnb_token, amount_readable
    )

    assert result_amount == amount_atomic
    assert result_decimals == 18


@mark.asyncio
async def test_bsc_chain_convert_amount_to_amount_atomic_token(
    bsc_chain: BscChain, w3: AsyncWeb3
):
    amount_atomic = 1250000000000000000
    amount_readable = AmountReadable("125000000.000000000010")

    token_contract = mock.Mock()
    token_contract.functions.decimals.return_value.call = mock.AsyncMock(
        return_value=10
    )
    w3.eth.contract.return_value = token_contract

    (
        result_amount_atomic,
        result_decimals,
    ) = await bsc_chain.convert_amount_to_amount_atomic(usdt_token, amount_readable)

    token_contract.functions.decimals.return_value.call.assert_called_once()

    assert result_amount_atomic == amount_atomic
    assert result_decimals == 10


@mark.asyncio
async def test_bsc_chain_convert_amount_atomic_to_amount_native_token(
    bsc_chain: BscChain, w3: AsyncWeb3
):
    amount_atomic = 1250000000000000000
    amount_readable = AmountReadable("1.25")

    result_amount, result_decimals = await bsc_chain.convert_amount_atomic_to_amount(
        bnb_token, amount_atomic
    )

    assert result_amount == amount_readable
    assert result_decimals == 18


@mark.asyncio
async def test_bsc_chain_convert_amount_atomic_to_amount_token(
    bsc_chain: BscChain, w3: AsyncWeb3
):
    amount_atomic = 1250000000000000000
    amount_readable = AmountReadable("125000000.0000000000")

    token_contract = mock.Mock()
    token_contract.functions.decimals.return_value.call = mock.AsyncMock(
        return_value=10
    )
    w3.eth.contract.return_value = token_contract

    result_amount, result_decimals = await bsc_chain.convert_amount_atomic_to_amount(
        usdt_token, amount_atomic
    )

    token_contract.functions.decimals.return_value.call.assert_called_once()

    assert result_amount == amount_readable
    assert result_decimals == 10
