from unittest import mock
from pytest import fixture, mark, raises
from api.shared.http_request.exception.failed_request import FailedRequest
from api.shared.http_request.http_request import HttpRequest
from api.token.infrastructure.coingecko.coingecko_token_repository import (
    CoingeckoTokenRepository,
    Configuration,
    GetFromAddressToken,
    GetFromAddressTokenMarketData,
    GetFromAddressTokenDetailPlatform,
    GetFromAddressTokenDetailPlatformImage,
    GetFromAddressTokenDetailPlatforms,
    GetFromAddressTokenUsdValue,
    CoinGeckoTokenUsdDateValue,
    GetFromAddressTokenEnText,
    GetFromAddressTokenLinks,
    GetFromAddressTokenDeveloperData,
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

    token_model = GetFromAddressToken(
        id="test_token",
        symbol="ttk",
        name="Test Token",
        detail_platforms=GetFromAddressTokenDetailPlatforms(
            binance_smart_chain=GetFromAddressTokenDetailPlatform(  # type: ignore
                decimal_place=18, contract_address=address
            )
        ),
        categories=["category1", "category2"],
        localization=GetFromAddressTokenEnText(en="Test Token"),
        description=GetFromAddressTokenEnText(en="This is a test token."),
        links=GetFromAddressTokenLinks(),
        image=GetFromAddressTokenDetailPlatformImage(
            small="https://testtoken.org/logo.png"
        ),
        market_data=GetFromAddressTokenMarketData(
            market_cap=GetFromAddressTokenUsdValue(usd=1000000),
            ath_change_percentage=GetFromAddressTokenUsdValue(usd=-50.0),
            ath_date=CoinGeckoTokenUsdDateValue(usd="2021-05-10T00:00:00.000Z"),
            atl_change_percentage=GetFromAddressTokenUsdValue(usd=1000.0),
            atl_date=CoinGeckoTokenUsdDateValue(usd="2020-03-13T00:00:00.000Z"),
            fully_diluted_valuation=GetFromAddressTokenUsdValue(usd=2000000),
            total_volume=GetFromAddressTokenUsdValue(usd=500000),
        ),
        developer_data=GetFromAddressTokenDeveloperData(),
        tickers=[],
    )

    http_request.get.return_value = token_model

    result = await repository.get_by_address(address)

    assert result is not None
    token_similarity, model = result
    assert token_similarity.id == f"bsc:{address}"
    assert token_similarity.name == "Test Token"
    assert token_similarity.display_name == "Test Token"
    assert token_similarity.ticker == "TTK"
    assert token_similarity.address == address
    assert token_similarity.description == "This is a test token."
    assert token_similarity.decimals == 18

    assert model == token_model

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


@mark.asyncio
async def test_coingecko_token_repository_get_from_address_display_name_format(
    repository: CoingeckoTokenRepository,
    http_request: HttpRequest,
):
    address = "0x1234567890abcdef1234567890abcdef12345678"

    http_request.get.return_value = GetFromAddressToken(
        id="test_token",
        symbol="ttk",
        name="Test Token (BNB Smart Chain)",
        detail_platforms=GetFromAddressTokenDetailPlatforms(
            binance_smart_chain=GetFromAddressTokenDetailPlatform(  # type: ignore
                decimal_place=18, contract_address=address
            )
        ),
        categories=["category1", "category2"],
        localization=GetFromAddressTokenEnText(en="Test Token"),
        description=GetFromAddressTokenEnText(en="This is a test token."),
        links=GetFromAddressTokenLinks(),
        image=GetFromAddressTokenDetailPlatformImage(
            small="https://testtoken.org/logo.png"
        ),
        market_data=GetFromAddressTokenMarketData(
            market_cap=GetFromAddressTokenUsdValue(usd=1000000),
            ath_change_percentage=GetFromAddressTokenUsdValue(usd=-50.0),
            ath_date=CoinGeckoTokenUsdDateValue(usd="2021-05-10T00:00:00.000Z"),
            atl_change_percentage=GetFromAddressTokenUsdValue(usd=1000.0),
            atl_date=CoinGeckoTokenUsdDateValue(usd="2020-03-13T00:00:00.000Z"),
            fully_diluted_valuation=GetFromAddressTokenUsdValue(usd=2000000),
            total_volume=GetFromAddressTokenUsdValue(usd=500000),
        ),
        developer_data=GetFromAddressTokenDeveloperData(),
        tickers=[],
    )

    result = await repository.get_by_address(address)

    assert result
    token_similarity, _ = result
    assert token_similarity.display_name == "Test Token"


@mark.asyncio
async def test_coingecko_token_repository_get_from_address_is_canonical(
    repository: CoingeckoTokenRepository,
    http_request: HttpRequest,
):
    address = "0x1234567890abcdef1234567890abcdef12345678"

    http_request.get.return_value = GetFromAddressToken(
        id="test_token",
        symbol="ttk",
        name="Binance-Peg Test Token",
        detail_platforms=GetFromAddressTokenDetailPlatforms(
            binance_smart_chain=GetFromAddressTokenDetailPlatform(  # type: ignore
                decimal_place=18, contract_address=address
            )
        ),
        categories=["category1", "category2"],
        localization=GetFromAddressTokenEnText(en="Test Token"),
        description=GetFromAddressTokenEnText(en="This is a test token."),
        links=GetFromAddressTokenLinks(),
        image=GetFromAddressTokenDetailPlatformImage(
            small="https://testtoken.org/logo.png"
        ),
        market_data=GetFromAddressTokenMarketData(
            market_cap=GetFromAddressTokenUsdValue(usd=1000000),
            ath_change_percentage=GetFromAddressTokenUsdValue(usd=-50.0),
            ath_date=CoinGeckoTokenUsdDateValue(usd="2021-05-10T00:00:00.000Z"),
            atl_change_percentage=GetFromAddressTokenUsdValue(usd=1000.0),
            atl_date=CoinGeckoTokenUsdDateValue(usd="2020-03-13T00:00:00.000Z"),
            fully_diluted_valuation=GetFromAddressTokenUsdValue(usd=2000000),
            total_volume=GetFromAddressTokenUsdValue(usd=500000),
        ),
        developer_data=GetFromAddressTokenDeveloperData(),
        tickers=[],
    )

    result = await repository.get_by_address(address)

    assert result
    token_similarity, _ = result
    assert token_similarity.is_canonical == 1
