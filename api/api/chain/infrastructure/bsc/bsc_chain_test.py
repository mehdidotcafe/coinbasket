from unittest import mock
from api.address.address import Address
from api.chain.transaction_receipt_parser import TransactionReceiptParser
from hexbytes import HexBytes
from api.chain.balance import BalanceAtomic
from api.chain.chain import ParsedReceipt
from api.chain.exception.insufficient_balance import InsufficientBalance
from pytest import fixture, mark, raises
from decimal import Decimal
from web3 import AsyncWeb3
from web3.types import Wei
from web3.eth import AsyncEth


from api.protocol.token import Token
from api.protocol.fixture.token import eth_token, usdt_token
from api.chain.infrastructure.bsc.bsc_chain import BscChain

from api.protocol.fixture.token import bnb_token, wbnb_token


@fixture
def w3():
    w3 = mock.Mock(spec=AsyncWeb3)

    w3.eth = mock.Mock(spec=AsyncEth)

    w3.to_checksum_address.side_effect = lambda x: f"{x}_checksum"
    w3.eth._gas_price = mock.AsyncMock(return_value=Wei(1_000_000_000))
    w3.eth._chain_id = mock.AsyncMock(return_value=42)

    return w3


@fixture
def base_token():
    return bnb_token


@fixture
def transaction_receipt_parser():
    return mock.Mock(spec=TransactionReceiptParser)


@fixture
def bsc_chain(
    w3: AsyncWeb3,
    transaction_receipt_parser: TransactionReceiptParser,
):
    return BscChain(
        w3=w3,
        transaction_receipt_parser=transaction_receipt_parser,
    )


@fixture
def address():
    return Address("0x1234567890abcdef1234567890abcdef12345678")


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
    address = Address("0x1234567890abcdef1234567890abcdef12345678")
    w3.eth.get_balance.return_value = Wei(1000000000000000000)
    w3.from_wei.return_value = Decimal("1")

    balance = await bsc_chain.get_native_token_balance(address)

    assert balance.amount == Decimal("1")
    assert balance.asset == base_token

    w3.eth.get_balance.assert_called_once_with(
        "0x1234567890abcdef1234567890abcdef12345678_checksum",
    )
    w3.from_wei.assert_called_once_with(
        Wei(1000000000000000000),
        "ether",
    )


@mark.asyncio
async def test_bsc_chain_get_available_balance_insufficient_balance(
    bsc_chain: BscChain, w3: AsyncWeb3
):
    address = Address("0x1234567890abcdef1234567890abcdef12345678")

    w3.eth.get_balance.return_value = Wei(100)
    w3.from_wei.side_effect = lambda x, _unit: x

    with raises(InsufficientBalance):
        await bsc_chain.get_native_token_available_balance(address)


@mark.asyncio
async def test_bsc_chain_get_available_balance(
    bsc_chain: BscChain, w3: AsyncWeb3, base_token: Token
):
    address = Address("0x1234567890abcdef1234567890abcdef12345678")
    w3.eth.get_balance.return_value = Wei(1000000000000000000)
    w3.from_wei.side_effect = lambda x, _unit: x

    balance = await bsc_chain.get_native_token_available_balance(address)

    assert balance.amount == Decimal(
        1000000000000000000 - (1_000_000_000 * 200_000 * 20)
    )
    assert balance.asset == base_token

    w3.eth.get_balance.assert_called_once_with(
        "0x1234567890abcdef1234567890abcdef12345678_checksum",
    )


@mark.asyncio
async def test_bsc_chain_get_asset_balance(bsc_chain: BscChain, w3: AsyncWeb3):
    address = Address("0x1234567890abcdef1234567890abcdef12345678")
    token = Token(
        id="bsc:0xabcdefabcdefabcdefabcdefabcdefabcdefabcdef",
        name="Fake token",
        display_name="Fake token",
        ticker="FTK",
        address="0xabcdefabcdefabcdefabcdefabcdefabcdefabcdef",
        description="Fake token for testing",
        decimals=18,
        categories=[],
        logo_uri=None,
    )

    token_contract = mock.Mock()
    token_contract.functions.balanceOf.return_value.call = mock.AsyncMock(
        return_value=1 * 10**18
    )
    w3.eth.contract.return_value = token_contract

    balance = await bsc_chain.get_asset_balance(address, token)

    assert balance == BalanceAtomic[Token](
        asset=token, amount=Decimal("1"), amount_atomic=1 * 10**18, decimals=18
    )
    token_contract.functions.balanceOf.return_value.call.assert_called_once()


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
        description="Fake token for testing",
        decimals=18,
        categories=[],
        logo_uri=None,
    )

    token_contract = mock.Mock()
    token_contract.functions.balanceOf.return_value.call = mock.AsyncMock(
        return_value=1 * 10**18
    )
    w3.eth.contract.return_value = token_contract

    balance = await bsc_chain.get_address_asset_balance(address, token)

    assert balance == BalanceAtomic[Token](
        asset=token, amount=Decimal("1"), amount_atomic=1 * 10**18, decimals=18
    )

    token_contract.functions.balanceOf.assert_called_once_with(
        "0x2B5616d51Cd04862a6BD16cE63B47364A2261125_checksum",
    )
    token_contract.functions.balanceOf.return_value.call.assert_called_once()


def test_bsc_chain_get_base_token(bsc_chain: BscChain, base_token: Token):
    base_token_result = bsc_chain.get_base_token()

    assert base_token_result == base_token


def test_bsc_chain_get_wrapped_base_token(bsc_chain: BscChain):
    base_token_result = bsc_chain.get_wrapped_base_token()

    assert base_token_result == wbnb_token


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
    transaction_receipt_parser: TransactionReceiptParser,
    address: Address,
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

    transaction_receipt_parser.parse_receipt.return_value = parsed_receipt

    result = await bsc_chain.parse_transaction_receipt(
        address=address,
        sell_asset=sell_token,
        buy_asset=buy_token,
        transaction_hash=transaction_hash,
    )

    transaction_receipt_parser.parse_receipt.assert_called_once_with(
        address=address,
        sell_asset=sell_token,
        buy_asset=buy_token,
        transaction_hash=transaction_hash,
    )

    assert result == parsed_receipt
