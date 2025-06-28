from decimal import Decimal
from unittest import mock
from eth_typing import HexStr
from hexbytes import HexBytes
from invest_agent.chain.balance import Balance
from invest_agent.chain.chain import Chain, Gas, TransactionFailure
from invest_agent.chain.contract import Contract
from invest_agent.investment.basket_investment import Bid
from invest_agent.investment.infrastructure.zero_x.fee import Fee, Fees
from invest_agent.investment.infrastructure.zero_x.price import Allowance, Issues, Price
from invest_agent.investment.infrastructure.zero_x.quote import (
    InsufficientLiquidityQuote,
    Permit2,
    Quote,
    QuoteResult,
    Transaction,
)
from invest_agent.investment.exchange.exchange import ConvertedBalance, Wallet
from invest_agent.investment.infrastructure.zero_x.zero_x_api_client import (
    ZeroXApiClient,
)
from invest_agent.investment.infrastructure.zero_x.zero_x_swapper import (
    Configuration,
    ZeroXSwapper,
)
from invest_agent.investment.investment_parameters import InvestmentParameters
from invest_agent.investment.investment_plan import InvestmentPlan, InvestmentPlanStep
from pytest import fixture, mark
from protocol.fixture.token import bnb_token, eth_token, usdt_token, sol_token

from web3 import AsyncWeb3
from web3.eth import Eth
from eth_account.signers.local import LocalAccount


@fixture
def w3():
    w3 = mock.Mock(spec=AsyncWeb3)

    w3.eth = mock.Mock(spec=Eth)

    account = mock.Mock(spec=LocalAccount)
    account.address = "0x1234567890abcdef1234567890abcdef12345678"

    w3.eth.account.from_key.return_value = account
    w3.to_checksum_address.side_effect = lambda x: x
    w3.to_wei.return_value = 1000000000000000000

    return w3


@fixture
def zero_x_api_client():
    return mock.Mock(spec=ZeroXApiClient)


@fixture
def chain():
    return mock.Mock(spec=Chain)


@fixture
def contract():
    contract = mock.Mock(spec=Contract)

    contract.get_decimals.return_value = Decimal("18")

    return contract


@fixture
def configuration():
    return {
        "bsc_rpc_url": "https://bsc-dataseed.binance.org/",
        "private_key": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
    }


@fixture
def investment_parameters():
    return InvestmentParameters(
        slippage_tolerance_in_percentage=Decimal("1"),
    )


@mark.asyncio
async def test_zero_x_swapper_execute_investment_plan_without_permit2_signature(
    zero_x_api_client: ZeroXApiClient,
    chain: Chain,
    contract: Contract,
    configuration: Configuration,
    w3: AsyncWeb3,
    investment_parameters: InvestmentParameters,
):
    zero_x_swapper = ZeroXSwapper(
        api_client=zero_x_api_client,
        chain=chain,
        contract=contract,
        configuration=configuration,
        w3=w3,
    )
    investment_plan = InvestmentPlan(
        steps=[
            InvestmentPlanStep(
                token=eth_token,
                sell_balance=Balance(
                    token=bnb_token,
                    amount=Decimal("1"),
                ),
            ),
        ],
        sell_total_balance=Balance(token=bnb_token, amount=Decimal("1")),
    )

    chain.is_native_token.return_value = True
    chain.get_chain_id.return_value = 42

    zero_x_api_client.get_quote.return_value = QuoteResult(
        root=Quote(
            permit2=None,
            transaction=Transaction(
                to="0xABcdEFABcdEFabcdEfAbCdefabcdeFABcDEFabCD",
                data="0x1234567890abcdef1234567890abcdef12345678",
                gas="21000",
                gasPrice="1000000000",
                value="1000000000000000000",
            ),
            liquidityAvailable=True,
            buyAmount="254516995428172740",
            buyToken="0x2170ed0880ac9a755fd29b2688956bd959f933f8",
            sellAmount="1000000000000000000",
            sellToken="0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
            fees=Fees(
                integratorFee=None,
                zeroExFee=Fee(
                    amount="382349016667264",
                    token="0x2170ed0880ac9a755fd29b2688956bd959f933f8",
                    type="volume",
                ),
                gasFee=None,
            ),
        )
    )
    chain.sign_send_wait_transaction.return_value = {"logs": []}

    await zero_x_swapper.execute_investment_plan(investment_plan, investment_parameters)

    zero_x_api_client.get_quote.assert_called_once_with(
        taker="0x1234567890abcdef1234567890abcdef12345678",
        chain_id=42,
        sell_token="0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
        buy_token="0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
        amount=1000000000000000000,
        slippage_bps=Decimal("100"),
        investment_parameters=investment_parameters,
    )
    chain.sign_send_wait_transaction.assert_called_once_with(
        gas=Gas(gas=21000, gas_price=1000000000),
        to_address="0xABcdEFABcdEFabcdEfAbCdefabcdeFABcDEFabCD",
        encoded_input="0x1234567890abcdef1234567890abcdef12345678",
        amount=1000000000000000000,
    )


@mark.asyncio
async def test_zero_x_swapper_execute_investment_plan_with_permit2_signature(
    zero_x_api_client: ZeroXApiClient,
    chain: Chain,
    contract: Contract,
    configuration: Configuration,
    w3: AsyncWeb3,
    investment_parameters: InvestmentParameters,
):
    zero_x_swapper = ZeroXSwapper(
        api_client=zero_x_api_client,
        chain=chain,
        contract=contract,
        configuration=configuration,
        w3=w3,
    )
    investment_plan = InvestmentPlan(
        steps=[
            InvestmentPlanStep(
                token=eth_token,
                sell_balance=Balance(
                    token=bnb_token,
                    amount=Decimal("1"),
                ),
            ),
        ],
        sell_total_balance=Balance(token=bnb_token, amount=Decimal("1")),
    )

    chain.is_native_token.return_value = True
    chain.get_chain_id.return_value = 42

    zero_x_api_client.get_quote.return_value = QuoteResult(
        root=Quote(
            permit2=Permit2(
                eip721={
                    "types": {
                        "EIP712Domain": [
                            {"name": "name", "type": "string"},
                            {"name": "version", "type": "string"},
                            {"name": "chainId", "type": "uint256"},
                            {"name": "verifyingContract", "type": "address"},
                        ],
                        "Permit": [
                            {"name": "spender", "type": "address"},
                            {"name": "tokenId", "type": "uint256"},
                            {"name": "nonce", "type": "uint256"},
                            {"name": "deadline", "type": "uint256"},
                        ],
                    },
                    "primaryType": "Permit",
                    "domain": {
                        "name": "MyNFT",
                        "version": "1",
                        "chainId": 1,
                        "verifyingContract": "0xCcCCccccCCCCcCCCCCCcCcCccCcCCCcCcccccccC",
                    },
                    "message": {
                        "spender": "0xAb8483F64d9C6d1EcF9b849Ae677dD3315835Cb2",
                        "tokenId": 1234,
                        "nonce": 1,
                        "deadline": 1754884800,
                    },
                }
            ),
            transaction=Transaction(
                to="0xABcdEFABcdEFabcdEfAbCdefabcdeFABcDEFabCD",
                data="0x1234567890abcdef1234567890abcdef12345678",
                gas="21000",
                gasPrice="1000000000",
                value="1000000000000000000",
            ),
            liquidityAvailable=True,
            buyAmount="254516995428172740",
            buyToken="0x2170ed0880ac9a755fd29b2688956bd959f933f8",
            sellAmount="1000000000000000000",
            sellToken="0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
            fees=Fees(
                integratorFee=None,
                zeroExFee=Fee(
                    amount="382349016667264",
                    token="0x2170ed0880ac9a755fd29b2688956bd959f933f8",
                    type="volume",
                ),
                gasFee=None,
            ),
        )
    )

    w3.eth.account.sign_typed_data.return_value = mock.Mock(
        signature=HexBytes("0x12890438482abdbf")
    )
    await zero_x_swapper.execute_investment_plan(investment_plan, investment_parameters)

    chain.sign_send_wait_transaction.assert_called_once_with(
        gas=mock.ANY,
        to_address=mock.ANY,
        amount=mock.ANY,
        encoded_input=f"0x{'0x1234567890abcdef1234567890abcdef12345678'[2:]}{'0x0000000000000000000000000000000000000000000000000000000000000008'[2:]}{'0x12890438482abdbf'[2:]}",  # Permit2 signature
    )


@mark.asyncio
async def test_zero_x_swapper_execute_investment_plan_bids(
    zero_x_api_client: ZeroXApiClient,
    chain: Chain,
    contract: Contract,
    configuration: Configuration,
    w3: AsyncWeb3,
    investment_parameters: InvestmentParameters,
):
    zero_x_swapper = ZeroXSwapper(
        api_client=zero_x_api_client,
        chain=chain,
        contract=contract,
        configuration=configuration,
        w3=w3,
    )
    investment_plan = InvestmentPlan(
        steps=[
            InvestmentPlanStep(
                token=eth_token,
                sell_balance=Balance(
                    token=bnb_token,
                    amount=Decimal("1"),
                ),
            )
        ],
        sell_total_balance=Balance(token=bnb_token, amount=Decimal("3")),
    )

    chain.is_native_token.return_value = True
    chain.get_chain_id.return_value = 42

    zero_x_api_client.get_quote.return_value = QuoteResult(
        root=Quote(
            liquidityAvailable=True,
            permit2=None,
            transaction=Transaction(
                to="0x779a74436eda060911b2c4f209d34ea155f3df09",
                data="0x1fff991f000000000000000000000000b404993a0129379d1d90e5a52d06652ffd0ae7c30000000000000000000000002170ed0880ac9a755fd29b2688956bd959f933f8000000000000000000000000000000000000000000000000037f2b9015013b3400000000000000000000000000000000000000000000000000000000000000a0b64bb5e2694f3cb22e67414200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000001c000000000000000000000000000000000000000000000000000000000000002e00000000000000000000000000000000000000000000000000000000000000380000000000000000000000000000000000000000000000000000000000000010438c9c147000000000000000000000000eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee0000000000000000000000000000000000000000000000000000000000002710000000000000000000000000bb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c000000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000a00000000000000000000000000000000000000000000000000000000000000024d0e30db00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000e48d68a156000000000000000000000000779a74436eda060911b2c4f209d34ea155f3df09000000000000000000000000000000000000000000000000000000000000271000000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002cbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c010000642170ed0880ac9a755fd29b2688956bd959f933f80000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000064c876d21d000000000000000000000000f5c4f3dc02c3fb9279495a8fef7b0741da9561570000000000000000000000002170ed0880ac9a755fd29b2688956bd959f933f80000000000000000000000000000000000000000000000000389959a869b450100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000012438c9c1470000000000000000000000002170ed0880ac9a755fd29b2688956bd959f933f8000000000000000000000000000000000000000000000000000000000000000f0000000000000000000000002170ed0880ac9a755fd29b2688956bd959f933f8000000000000000000000000000000000000000000000000000000000000002400000000000000000000000000000000000000000000000000000000000000a00000000000000000000000000000000000000000000000000000000000000044a9059cbb000000000000000000000000ad01c20d5886137e056775af56915de824c8fce500000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                gas="322930",
                gasPrice="100000000",
                value="1000000000000000000",
            ),
            buyAmount="254516995428172740",
            buyToken="0x2170ed0880ac9a755fd29b2688956bd959f933f8",
            sellAmount="1000000000000000000",
            sellToken="0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
            fees=Fees(
                integratorFee=None,
                zeroExFee=Fee(
                    amount="382349016667264",
                    token="0x2170ed0880ac9a755fd29b2688956bd959f933f8",
                    type="volume",
                ),
                gasFee=None,
            ),
        )
    )

    bids = await zero_x_swapper.execute_investment_plan(
        investment_plan, investment_parameters
    )

    assert bids == [
        Bid(
            token=eth_token,
            sell_balance=Balance(
                token=bnb_token,
                amount=Decimal("1.0"),
            ),
            buy_balance=Balance(
                token=eth_token,
                amount=Decimal("0.25451699542817274"),
            ),
        ),
    ]


@mark.asyncio
async def test_zero_x_swapper_execute_investment_plan_retry(
    zero_x_api_client: ZeroXApiClient,
    chain: Chain,
    contract: Contract,
    configuration: Configuration,
    w3: AsyncWeb3,
    investment_parameters: InvestmentParameters,
):
    zero_x_swapper = ZeroXSwapper(
        api_client=zero_x_api_client,
        chain=chain,
        contract=contract,
        configuration=configuration,
        w3=w3,
    )
    investment_plan = InvestmentPlan(
        steps=[
            InvestmentPlanStep(
                token=eth_token,
                sell_balance=Balance(
                    token=bnb_token,
                    amount=Decimal("1"),
                ),
            )
        ],
        sell_total_balance=Balance(token=bnb_token, amount=Decimal("3")),
    )

    chain.is_native_token.return_value = True
    chain.get_chain_id.return_value = 42

    zero_x_api_client.get_quote.return_value = QuoteResult(
        root=Quote(
            liquidityAvailable=True,
            permit2=None,
            transaction=Transaction(
                to="0x779a74436eda060911b2c4f209d34ea155f3df09",
                data="0x1fff991f000000000000000000000000b404993a0129379d1d90e5a52d06652ffd0ae7c30000000000000000000000002170ed0880ac9a755fd29b2688956bd959f933f8000000000000000000000000000000000000000000000000037f2b9015013b3400000000000000000000000000000000000000000000000000000000000000a0b64bb5e2694f3cb22e67414200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000001c000000000000000000000000000000000000000000000000000000000000002e00000000000000000000000000000000000000000000000000000000000000380000000000000000000000000000000000000000000000000000000000000010438c9c147000000000000000000000000eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee0000000000000000000000000000000000000000000000000000000000002710000000000000000000000000bb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c000000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000a00000000000000000000000000000000000000000000000000000000000000024d0e30db00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000e48d68a156000000000000000000000000779a74436eda060911b2c4f209d34ea155f3df09000000000000000000000000000000000000000000000000000000000000271000000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002cbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c010000642170ed0880ac9a755fd29b2688956bd959f933f80000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000064c876d21d000000000000000000000000f5c4f3dc02c3fb9279495a8fef7b0741da9561570000000000000000000000002170ed0880ac9a755fd29b2688956bd959f933f80000000000000000000000000000000000000000000000000389959a869b450100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000012438c9c1470000000000000000000000002170ed0880ac9a755fd29b2688956bd959f933f8000000000000000000000000000000000000000000000000000000000000000f0000000000000000000000002170ed0880ac9a755fd29b2688956bd959f933f8000000000000000000000000000000000000000000000000000000000000002400000000000000000000000000000000000000000000000000000000000000a00000000000000000000000000000000000000000000000000000000000000044a9059cbb000000000000000000000000ad01c20d5886137e056775af56915de824c8fce500000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                gas="322930",
                gasPrice="100000000",
                value="1000000000000000000",
            ),
            buyAmount="254516995428172740",
            buyToken="0x2170ed0880ac9a755fd29b2688956bd959f933f8",
            sellAmount="1000000000000000000",
            sellToken="0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
            fees=Fees(
                integratorFee=None,
                zeroExFee=Fee(
                    amount="382349016667264",
                    token="0x2170ed0880ac9a755fd29b2688956bd959f933f8",
                    type="volume",
                ),
                gasFee=None,
            ),
        )
    )

    chain.sign_send_wait_transaction.side_effect = TransactionFailure()

    await zero_x_swapper.execute_investment_plan(investment_plan, investment_parameters)

    assert chain.sign_send_wait_transaction.call_count == 5


@mark.asyncio
async def test_zero_x_swapper_execute_investment_plan_no_liquidity(
    zero_x_api_client: ZeroXApiClient,
    chain: Chain,
    contract: Contract,
    configuration: Configuration,
    w3: AsyncWeb3,
    investment_parameters: InvestmentParameters,
):
    zero_x_swapper = ZeroXSwapper(
        api_client=zero_x_api_client,
        chain=chain,
        contract=contract,
        configuration=configuration,
        w3=w3,
    )
    investment_plan = InvestmentPlan(
        steps=[
            InvestmentPlanStep(
                token=eth_token,
                sell_balance=Balance(
                    token=bnb_token,
                    amount=Decimal("1"),
                ),
            )
        ],
        sell_total_balance=Balance(token=bnb_token, amount=Decimal("3")),
    )
    chain.is_native_token.return_value = True
    chain.get_chain_id.return_value = 42

    zero_x_api_client.get_quote.return_value = QuoteResult(
        root=InsufficientLiquidityQuote(
            liquidityAvailable=False,
        )
    )

    chain.sign_send_wait_transaction.side_effect = TransactionFailure()

    bids = await zero_x_swapper.execute_investment_plan(
        investment_plan, investment_parameters
    )

    assert not bids


@mark.asyncio
async def test_zero_x_swapper_execute_divestment_plan(
    zero_x_api_client: ZeroXApiClient,
    chain: Chain,
    contract: Contract,
    configuration: Configuration,
    w3: AsyncWeb3,
    investment_parameters: InvestmentParameters,
):
    zero_x_swapper = ZeroXSwapper(
        api_client=zero_x_api_client,
        chain=chain,
        contract=contract,
        configuration=configuration,
        w3=w3,
    )
    divestment_plan = InvestmentPlan(
        steps=[
            InvestmentPlanStep(
                token=bnb_token,
                sell_balance=Balance(
                    token=eth_token,
                    amount=Decimal("1"),
                ),
            )
        ],
        sell_total_balance=Balance(token=bnb_token, amount=Decimal("0")),
    )

    chain.is_native_token.return_value = True
    chain.get_chain_id.return_value = 42

    zero_x_api_client.get_price.return_value = Price(
        issues=Issues(),
        buyAmount="254516995428172740",
        sellAmount="1000000000000000000",
        buyToken="0x2170ed0880ac9a755fd29b2688956bd959f933f8",
        sellToken="0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
        fees=Fees(),
    )
    zero_x_api_client.get_quote.return_value = QuoteResult(
        root=Quote(
            permit2=None,
            transaction=Transaction(
                to="0xABcdEFABcdEFabcdEfAbCdefabcdeFABcDEFabCD",
                data="0x1234567890abcdef1234567890abcdef12345678",
                gas="21000",
                gasPrice="1000000000",
                value="0",
            ),
            liquidityAvailable=True,
            buyAmount="328938894889",
            buyToken="0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
            sellAmount="1000000000000000000",
            sellToken="0x2170ed0880ac9a755fd29b2688956bd959f933f8",
            fees=Fees(
                integratorFee=None,
                zeroExFee=Fee(
                    amount="382349016667264",
                    token="0x2170ed0880ac9a755fd29b2688956bd959f933f8",
                    type="volume",
                ),
                gasFee=None,
            ),
        )
    )
    chain.sign_send_wait_transaction.return_value = {"logs": []}

    await zero_x_swapper.execute_divestment_plan(divestment_plan, investment_parameters)

    zero_x_api_client.get_quote.assert_called_once_with(
        taker="0x1234567890abcdef1234567890abcdef12345678",
        chain_id=42,
        sell_token="0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
        buy_token="0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
        amount=1000000000000000000,
        sell_entire_balance=True,
        slippage_bps=Decimal("100"),
        investment_parameters=investment_parameters,
    )
    zero_x_api_client.get_price.assert_called_once_with(
        taker="0x1234567890abcdef1234567890abcdef12345678",
        chain_id=42,
        sell_token="0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
        buy_token="0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
        amount=1000000000000000000,
        sell_entire_balance=True,
        slippage_bps=Decimal("100"),
        investment_parameters=investment_parameters,
    )
    chain.sign_send_wait_transaction.assert_called_once_with(
        gas=Gas(gas=21000, gas_price=1000000000),
        to_address="0xABcdEFABcdEFabcdEfAbCdefabcdeFABcDEFabCD",
        encoded_input="0x1234567890abcdef1234567890abcdef12345678",
        amount=0,
    )


@mark.asyncio
async def test_zero_x_swapper_execute_divestment_plan_with_allowance(
    zero_x_api_client: ZeroXApiClient,
    chain: Chain,
    contract: Contract,
    configuration: Configuration,
    w3: AsyncWeb3,
    investment_parameters: InvestmentParameters,
):
    zero_x_swapper = ZeroXSwapper(
        api_client=zero_x_api_client,
        chain=chain,
        contract=contract,
        configuration=configuration,
        w3=w3,
    )
    divestment_plan = InvestmentPlan(
        steps=[
            InvestmentPlanStep(
                token=bnb_token,
                sell_balance=Balance(
                    token=eth_token,
                    amount=Decimal("1"),
                ),
            ),
        ],
        sell_total_balance=Balance(token=bnb_token, amount=Decimal("0")),
    )

    chain.is_native_token.return_value = False
    chain.get_chain_id.return_value = 42

    token_contract = mock.Mock()
    token_contract.functions.decimals.return_value.call = mock.AsyncMock(
        return_value=18
    )

    contract.make_approve_transaction_input.return_value = HexStr("0x29404c3b")

    w3.eth.contract.return_value = token_contract

    zero_x_api_client.get_price.return_value = Price(
        issues=Issues(
            allowance=Allowance(
                spender="0x694e49f3F7a24387299D619A2931Ee3A763Dc760",
            )
        ),
        buyAmount="254516995428172740",
        sellAmount="1000000000000000000",
        buyToken="0x2170ed0880ac9a755fd29b2688956bd959f933f8",
        sellToken="0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
        fees=Fees(),
    )
    zero_x_api_client.get_quote.return_value = QuoteResult(
        root=Quote(
            permit2=None,
            transaction=Transaction(
                to="0xABcdEFABcdEFabcdEfAbCdefabcdeFABcDEFabCD",
                data="0x1234567890abcdef1234567890abcdef12345678",
                gas="21000",
                gasPrice="1000000000",
                value="0",
            ),
            liquidityAvailable=True,
            buyAmount="328938894889",
            buyToken="0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
            sellAmount="1000000000000000000",
            sellToken="0x2170ed0880ac9a755fd29b2688956bd959f933f8",
            fees=Fees(
                integratorFee=None,
                zeroExFee=Fee(
                    amount="382349016667264",
                    token="0x2170ed0880ac9a755fd29b2688956bd959f933f8",
                    type="volume",
                ),
                gasFee=None,
            ),
        )
    )
    chain.sign_send_wait_transaction.return_value = {"logs": []}

    await zero_x_swapper.execute_divestment_plan(divestment_plan, investment_parameters)

    contract.make_approve_transaction_input.assert_called_once_with(
        token_address="0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
        spender_address="0x694e49f3F7a24387299D619A2931Ee3A763Dc760",
        amount=Decimal(
            115792089237316195423570985008687907853269984665640564039457584007913129639935
        ),
    )
    chain.assert_has_calls(
        [
            mock.call.sign_send_wait_transaction(
                amount=0,
                encoded_input="0x29404c3b",
                to_address="0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
            )
        ]
    )


@mark.asyncio
async def test_zero_x_swapper_get_wallet_in_token(
    zero_x_api_client: ZeroXApiClient,
    chain: Chain,
    contract: Contract,
    configuration: Configuration,
    w3: AsyncWeb3,
    investment_parameters: InvestmentParameters,
):
    token = usdt_token

    tokens_balance = [
        Balance(token=sol_token, amount=Decimal("1.0")),
        Balance(token=eth_token, amount=Decimal("4.0")),
        Balance(token=bnb_token, amount=Decimal("10.0")),
    ]

    zero_x_api_client.get_price.side_effect = [
        Price(
            issues=Issues(),
            buyAmount="300000000000000000000",
            sellAmount="1000000000000000000",
            buyToken=usdt_token.address,
            sellToken=sol_token.address,
            fees=Fees(),
        ),
        Price(
            issues=Issues(),
            buyAmount="1100000000000000000000",
            sellAmount="4000000000000000000",
            buyToken=usdt_token.address,
            sellToken=eth_token.address,
            fees=Fees(),
        ),
        Price(
            issues=Issues(),
            buyAmount="10000000000000000000",
            sellAmount="10000000000000000000",
            buyToken=usdt_token.address,
            sellToken=bnb_token.address,
            fees=Fees(),
        ),
    ]

    zero_x_swapper = ZeroXSwapper(
        api_client=zero_x_api_client,
        chain=chain,
        contract=contract,
        configuration=configuration,
        w3=w3,
    )

    wallet = await zero_x_swapper.get_wallet_in_token(
        tokens_balance, token, investment_parameters
    )

    assert wallet == Wallet(
        balances=[
            ConvertedBalance(
                sell_balance=Balance(token=sol_token, amount=Decimal("1.0")),
                buy_balance=Balance(token=usdt_token, amount=Decimal("300")),
            ),
            ConvertedBalance(
                sell_balance=Balance(token=eth_token, amount=Decimal("4.0")),
                buy_balance=Balance(token=usdt_token, amount=Decimal("1100.0")),
            ),
            ConvertedBalance(
                sell_balance=Balance(token=bnb_token, amount=Decimal("10.0")),
                buy_balance=Balance(token=usdt_token, amount=Decimal("10.0")),
            ),
        ],
        total_balance=Balance(token=usdt_token, amount=Decimal("1410.0")),
    )


@mark.asyncio
async def test_zero_x_swapper_get_wallet_in_token_same_token(
    zero_x_api_client: ZeroXApiClient,
    chain: Chain,
    contract: Contract,
    configuration: Configuration,
    w3: AsyncWeb3,
    investment_parameters: InvestmentParameters,
):
    token = usdt_token

    tokens_balance = [
        Balance(token=usdt_token, amount=Decimal("10.0")),
    ]

    zero_x_swapper = ZeroXSwapper(
        api_client=zero_x_api_client,
        chain=chain,
        contract=contract,
        configuration=configuration,
        w3=w3,
    )

    wallet = await zero_x_swapper.get_wallet_in_token(
        tokens_balance, token, investment_parameters
    )

    zero_x_swapper.api_client.get_price.assert_not_called()

    assert wallet == Wallet(
        balances=[
            ConvertedBalance(
                sell_balance=Balance(token=usdt_token, amount=Decimal("10.0")),
                buy_balance=Balance(token=usdt_token, amount=Decimal("10.0")),
            ),
        ],
        total_balance=Balance(token=usdt_token, amount=Decimal("10.0")),
    )


@mark.asyncio
async def test_zero_x_swapper_execute_divestment_plan_retry(
    zero_x_api_client: ZeroXApiClient,
    chain: Chain,
    contract: Contract,
    configuration: Configuration,
    w3: AsyncWeb3,
    investment_parameters: InvestmentParameters,
):
    zero_x_swapper = ZeroXSwapper(
        api_client=zero_x_api_client,
        chain=chain,
        contract=contract,
        configuration=configuration,
        w3=w3,
    )
    divestment_plan = InvestmentPlan(
        steps=[
            InvestmentPlanStep(
                token=bnb_token,
                sell_balance=Balance(
                    token=eth_token,
                    amount=Decimal("1"),
                ),
            ),
        ],
        sell_total_balance=Balance(token=bnb_token, amount=Decimal("0")),
    )

    chain.is_native_token.return_value = True
    chain.get_chain_id.return_value = 42

    zero_x_api_client.get_price.return_value = Price(
        issues=Issues(),
        buyAmount="254516995428172740",
        sellAmount="1000000000000000000",
        buyToken="0x2170ed0880ac9a755fd29b2688956bd959f933f8",
        sellToken="0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
        fees=Fees(),
    )
    zero_x_api_client.get_quote.return_value = QuoteResult(
        root=Quote(
            permit2=None,
            transaction=Transaction(
                to="0xABcdEFABcdEFabcdEfAbCdefabcdeFABcDEFabCD",
                data="0x1234567890abcdef1234567890abcdef12345678",
                gas="21000",
                gasPrice="1000000000",
                value="0",
            ),
            liquidityAvailable=True,
            buyAmount="328938894889",
            buyToken="0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
            sellAmount="1000000000000000000",
            sellToken="0x2170ed0880ac9a755fd29b2688956bd959f933f8",
            fees=Fees(
                integratorFee=None,
                zeroExFee=Fee(
                    amount="382349016667264",
                    token="0x2170ed0880ac9a755fd29b2688956bd959f933f8",
                    type="volume",
                ),
                gasFee=None,
            ),
        )
    )
    chain.sign_send_wait_transaction.side_effect = TransactionFailure()

    await zero_x_swapper.execute_divestment_plan(divestment_plan, investment_parameters)

    assert chain.sign_send_wait_transaction.call_count == 5


@mark.asyncio
async def test_zero_x_swapper_execute_divestment_plan_no_liquidity(
    zero_x_api_client: ZeroXApiClient,
    chain: Chain,
    contract: Contract,
    configuration: Configuration,
    w3: AsyncWeb3,
    investment_parameters: InvestmentParameters,
):
    zero_x_swapper = ZeroXSwapper(
        api_client=zero_x_api_client,
        chain=chain,
        contract=contract,
        configuration=configuration,
        w3=w3,
    )
    divestment_plan = InvestmentPlan(
        steps=[
            InvestmentPlanStep(
                token=bnb_token,
                sell_balance=Balance(
                    token=eth_token,
                    amount=Decimal("1"),
                ),
            ),
        ],
        sell_total_balance=Balance(token=bnb_token, amount=Decimal("0")),
    )

    chain.is_native_token.return_value = True
    chain.get_chain_id.return_value = 42

    zero_x_api_client.get_price.return_value = Price(
        issues=Issues(),
        buyAmount="254516995428172740",
        sellAmount="1000000000000000000",
        buyToken="0x2170ed0880ac9a755fd29b2688956bd959f933f8",
        sellToken="0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
        fees=Fees(),
    )
    zero_x_api_client.get_quote.return_value = QuoteResult(
        root=InsufficientLiquidityQuote(
            liquidityAvailable=False,
        )
    )
    bids = await zero_x_swapper.execute_divestment_plan(
        divestment_plan, investment_parameters
    )

    assert not bids
