from unittest import mock
from api.protocol.token import Token
from pytest import fixture, mark, raises
from api.shared.http_request.exception.failed_request import FailedRequest
from api.shared.http_request.http_request import HttpRequest
from api.token.infrastructure.coingecko.coingecko_token_repository import (
    CoingeckoTokenRepository,
    Configuration,
    GetFromAddressToken,
    GetFromAddressTokenDetailMarketCap,
    GetFromAddressTokenDetailMarketData,
    GetFromAddressTokenDetailPlatform,
    GetFromAddressTokenDetailPlatformImage,
    GetFromAddressTokenDetailPlatforms,
)


@fixture
def http_request():
    return mock.Mock(spec=HttpRequest)


@fixture
def repository(http_request: HttpRequest):
    config: Configuration = {
        "coingecko_base_url": "https://api.coingecko.com",
        "coingecko_api_key": "test_api_key",
    }
    return CoingeckoTokenRepository(http_request=http_request, config=config)


@mark.asyncio
async def test_coingecko_token_repository_get_from_address_token_not_found(
    repository: CoingeckoTokenRepository,
    http_request: HttpRequest,
):
    address = "NOT_FOUND_ADDRESS"

    http_request.get.side_effect = FailedRequest(status_code=404, response="Not found")

    result = await repository.get_by_address(address)

    assert result is None


@mark.asyncio
async def test_coingecko_token_repository_get_from_address_unhandled_error(
    repository: CoingeckoTokenRepository,
    http_request: HttpRequest,
):
    address = "SOME_ADDRESS"

    http_request.get.side_effect = FailedRequest(
        status_code=500, response="Server error"
    )

    with raises(Exception):
        await repository.get_by_address(address)


@mark.asyncio
async def test_coingecko_token_repository_get_from_address_success(
    repository: CoingeckoTokenRepository,
    http_request: HttpRequest,
):
    address = "0x1234567890abcdef1234567890abcdef12345678"

    http_request.get.return_value = GetFromAddressToken(
        id="test_token",
        symbol="ttk",
        name="Test Token",
        detail_platforms=GetFromAddressTokenDetailPlatforms(
            binance_smart_chain=GetFromAddressTokenDetailPlatform(  # type: ignore
                decimal_place=18, contract_address=address
            )
        ),
        categories=["category1", "category2"],
        description={"en": "This is a test token."},
        image=GetFromAddressTokenDetailPlatformImage(
            small="https://testtoken.org/logo.png"
        ),
        market_data=GetFromAddressTokenDetailMarketData(
            market_cap=GetFromAddressTokenDetailMarketCap(usd=1000000),
        ),
    )

    result = await repository.get_by_address(address)

    assert result == Token(
        id=f"bsc:{address}",
        name="Test Token",
        display_name="Test Token",
        ticker="TTK",
        address=address,
        description="This is a test token.",
        decimals=18,
        categories=["Decentralized Finance (DeFi)", "Dog-Themed"],
        logo_uri="https://testtoken.org/logo.png",
    )

    http_request.get.assert_called_once_with(
        {
            "url": f"https://api.coingecko.com/v3/coins/binance-smart-chain/contract/{address}",
            "headers": {
                "accept": "application/json",
                "x-cg-demo-api-key": "test_api_key",
            },
        },
        mock.ANY,
    )
