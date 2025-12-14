from unittest import mock
from protocol.token import Token
from pytest import fixture, mark, raises
from shared.http_request.exception.failed_request import FailedRequest
from shared.http_request.http_request import HttpRequest
from api.token.infrastructure.coingecko.coingecko_token_repository import (
    CoingeckoTokenRepository,
    Configuration,
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

    http_request.get.return_value = mock.Mock(
        id="test_token",
        symbol="TTK",
        name="Test Token",
        detail_platforms=mock.Mock(binance_smart_chain=mock.Mock(decimal_place=18)),
        categories=["category1", "category2"],
        description={"en": "This is a test token."},
        links={"homepage": ["https://testtoken.org"]},
        image=mock.Mock(thumb="https://testtoken.org/logo.png"),
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
        categories=["category1", "category2"],
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
