from decimal import Decimal
from unittest import mock
from api.investment.infrastructure.zero_x.exception.swap_validation_failed import (
    SwapValidationFailed,
)
from api.shared.http_request.exception.failed_request import FailedRequest
from api.shared.http_request.http_request import HttpRequest
from api.investment.infrastructure.zero_x.fee import Fee, Fees
from api.investment.infrastructure.zero_x.quote import (
    Quote,
    QuoteResult,
    Transaction,
)
from api.investment.infrastructure.zero_x.zero_x_api_client import (
    Configuration,
)
from api.investment.infrastructure.zero_x.zero_x_api_client import (
    ZeroXApiClient,
)
from api.investment.infrastructure.zero_x.price import Price, Issues, Allowance

from api.investment.investment_parameters import (
    IntegratorFee,
    InvestmentParametersWithFee,
)
from pytest import fixture, mark, raises


@fixture
def configuration():
    return {
        "zero_x_api_url": "https://api.0x.org",
        "zero_x_api_key": "test_api_key",
    }


@fixture
def http_request():
    return mock.Mock(spec=HttpRequest)


@fixture
def investment_parameters():
    return InvestmentParametersWithFee(
        slippage_tolerance_in_percentage=Decimal("1"),
        integrator_fee=IntegratorFee(
            recipient="0x1234567890abcdef1234567890abcdef12345678",
            value_in_percentage=Decimal("0.01"),
        ),
    )


@mark.asyncio
async def test_zero_x_api_client_get_price_success(
    configuration: Configuration,
    http_request: HttpRequest,
    investment_parameters: InvestmentParametersWithFee,
):
    client = ZeroXApiClient(configuration, http_request)

    taker = "0x1234567890abcdef1234567890abcdef12345678"
    chain_id = 1
    sell_token = "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd"
    buy_token = "0x1234567890abcdef1234567890abcdef12345678"
    amount = 1000000000000000000  # 1 ETH in wei

    expected_price = Price(
        issues=Issues(),
        buyAmount="254516995428172740",
        sellAmount="1000000000000000000",
        buyToken="0x2170ed0880ac9a755fd29b2688956bd959f933f8",
        sellToken="0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
        fees=Fees(),
        totalNetworkFee="21000000000000",
    )

    http_request.get.return_value = expected_price

    price = await client.get_price(
        taker=taker,
        chain_id=chain_id,
        sell_token=sell_token,
        buy_token=buy_token,
        amount=amount,
        slippage_bps=Decimal("100"),
        investment_parameters_with_fee=investment_parameters,
    )

    assert price == expected_price

    http_request.get.assert_called_once_with(
        {
            "url": "https://api.0x.org/swap/permit2/price",
            "params": {
                "chainId": 1,
                "sellToken": "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
                "buyToken": "0x1234567890abcdef1234567890abcdef12345678",
                "sellAmount": 1000000000000000000,
                "taker": "0x1234567890abcdef1234567890abcdef12345678",
                "slippageBps": 100,
                "swapFeeRecipient": "0x1234567890abcdef1234567890abcdef12345678",
                "swapFeeBps": 1,
            },
            "headers": {
                "Content-Type": "application/json",
                "0x-api-key": "test_api_key",
                "0x-version": "v2",
            },
        },
        Price,
    )


@mark.asyncio
async def test_zero_x_api_client_get_price_swap_validation_failed(
    configuration: Configuration,
    http_request: HttpRequest,
    investment_parameters: InvestmentParametersWithFee,
):
    client = ZeroXApiClient(configuration, http_request)

    taker = "0x1234567890abcdef1234567890abcdef12345678"
    chain_id = 1
    sell_token = "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd"
    buy_token = "0x1234567890abcdef1234567890abcdef12345678"
    amount = 1000000000000000000  # 1 ETH in wei

    http_request.get.side_effect = FailedRequest(
        status_code=400, response="{SWAP_VALIDATION_FAILED}"
    )

    with raises(SwapValidationFailed):
        await client.get_price(
            taker=taker,
            chain_id=chain_id,
            sell_token=sell_token,
            buy_token=buy_token,
            amount=amount,
            slippage_bps=Decimal("100"),
            investment_parameters_with_fee=investment_parameters,
        )


@mark.asyncio
async def test_zero_x_api_client_get_quote_success(
    configuration: Configuration,
    http_request: HttpRequest,
    investment_parameters: InvestmentParametersWithFee,
):
    client = ZeroXApiClient(configuration, http_request)

    taker = "0x5234567890abcdef1234567890abcdef12345678"
    chain_id = 1
    sell_token = "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd"
    buy_token = "0x1234567890abcdef1234567890abcdef12345678"
    amount = 1000000000000000000  # 1 ETH in wei

    expected_quote = Quote(
        permit2=None,
        issues=Issues(
            allowance=Allowance(
                spender="0xdefdefdefdefdefdefdefdefdefdefdefdefdefd",
            )
        ),
        transaction=Transaction(
            to="0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
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
        totalNetworkFee="21000000000000",
    )

    http_request.get.return_value = expected_quote

    quote = await client.get_quote(
        taker=taker,
        chain_id=chain_id,
        sell_token=sell_token,
        buy_token=buy_token,
        amount=amount,
        slippage_bps=Decimal("100"),
        investment_parameters_with_fee=investment_parameters,
    )

    assert quote == expected_quote

    http_request.get.assert_called_once_with(
        {
            "url": "https://api.0x.org/swap/permit2/quote",
            "params": {
                "chainId": 1,
                "sellToken": "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
                "buyToken": "0x1234567890abcdef1234567890abcdef12345678",
                "sellAmount": 1000000000000000000,
                "taker": "0x5234567890abcdef1234567890abcdef12345678",
                "slippageBps": 100,
                "swapFeeRecipient": "0x1234567890abcdef1234567890abcdef12345678",
                "swapFeeBps": 1,
            },
            "headers": {
                "Content-Type": "application/json",
                "0x-api-key": "test_api_key",
                "0x-version": "v2",
            },
        },
        QuoteResult,
    )
