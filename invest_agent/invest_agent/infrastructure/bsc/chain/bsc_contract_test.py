from decimal import Decimal
from unittest import mock
from pytest import fixture, mark
from web3 import AsyncWeb3
from web3.eth import AsyncEth

from invest_agent.infrastructure.bsc.chain.bsc_contract import BscContract


@fixture
def w3():
    w3 = mock.Mock(spec=AsyncWeb3)
    w3.to_checksum_address = mock.Mock(side_effect=lambda x: f"{x}_checksum")

    w3.eth = mock.Mock(spec=AsyncEth)

    return w3


@mark.asyncio
async def test_bsc_contract_get_decimals(w3: AsyncWeb3):
    contract = BscContract(w3=w3)

    token_address = "0x1234567890abcdef1234567890abcdef12345678"

    token_contract = mock.Mock()
    token_contract.functions.decimals.return_value.call = mock.AsyncMock(
        return_value=18
    )
    w3.eth.contract.return_value = token_contract

    decimals = await contract.get_decimals(token_address)

    assert decimals == 18

    w3.eth.contract.assert_called_once_with(
        address="0x1234567890abcdef1234567890abcdef12345678_checksum", abi=mock.ANY
    )
    token_contract.functions.decimals.return_value.call.assert_called_once()

    decimals_cached = await contract.get_decimals(token_address)

    assert decimals_cached == 18

    token_contract.functions.decimals.return_value.call.assert_called_once()


@mark.asyncio
async def test_bsc_contract_make_approve_transaction_input(w3: AsyncWeb3):
    contract = BscContract(w3=w3)

    token_address = "0x1234567890abcdef1234567890abcdef12345678"
    spender_address = "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd"
    amount = Decimal(1000)

    token_contract = mock.Mock()
    token_contract.functions.approve.return_value._encode_transaction_data = mock.Mock(
        return_value="encoded_transaction_data"
    )
    w3.eth.contract.return_value = token_contract

    encoded_input = contract.make_approve_transaction_input(
        token_address, spender_address, amount
    )

    assert encoded_input == "encoded_transaction_data"

    w3.eth.contract.assert_called_once_with(
        address="0x1234567890abcdef1234567890abcdef12345678_checksum", abi=mock.ANY
    )
    token_contract.functions.approve.assert_called_once_with(
        "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd_checksum", amount
    )
