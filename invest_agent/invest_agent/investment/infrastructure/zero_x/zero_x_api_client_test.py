from unittest import mock
from invest_agent.http_request.http_request import HttpRequest
from invest_agent.investment.infrastructure.zero_x.fee import Fee, Fees
from invest_agent.investment.infrastructure.zero_x.quote import (
    Quote,
    QuoteResult,
    Transaction,
)
from invest_agent.investment.infrastructure.zero_x.zero_x_api_client import (
    Configuration,
)
from invest_agent.investment.infrastructure.zero_x.zero_x_api_client import (
    ZeroXApiClient,
)
from invest_agent.investment.infrastructure.zero_x.price import Price, Issues

from pytest import fixture


@fixture
def configuration():
    return {
        "zero_x_api_url": "https://api.0x.org",
        "zero_x_api_key": "test_api_key",
    }


@fixture
def http_request():
    return mock.Mock(spec=HttpRequest)


def test_zero_x_api_client_get_price_success(
    configuration: Configuration, http_request: HttpRequest[Price]
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
    )

    http_request.get.return_value = expected_price

    price = client.get_price(taker, chain_id, sell_token, buy_token, amount)

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
            },
            "headers": {
                "Content-Type": "application/json",
                "0x-api-key": "test_api_key",
                "0x-version": "v2",
            },
        },
        Price,
    )


def test_zero_x_api_client_get_quote_success(
    configuration: Configuration, http_request: HttpRequest[QuoteResult]
):
    client = ZeroXApiClient(configuration, http_request)

    taker = "0x5234567890abcdef1234567890abcdef12345678"
    chain_id = 1
    sell_token_address = "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd"
    buy_token = "0x1234567890abcdef1234567890abcdef12345678"
    amount = 1000000000000000000  # 1 ETH in wei

    expected_quote = Quote(
        permit2=None,
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
    )

    http_request.get.return_value = expected_quote

    quote = client.get_quote(taker, chain_id, sell_token_address, buy_token, amount)

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
            },
            "headers": {
                "Content-Type": "application/json",
                "0x-api-key": "test_api_key",
                "0x-version": "v2",
            },
        },
        QuoteResult,
    )
