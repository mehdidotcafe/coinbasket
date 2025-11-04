from unittest import mock
from pytest import fixture, mark
from data_agent.ingestion.id.id_generator import IdGenerator
from shared.http_request.http_request import HttpRequest
from data_agent.ingestion.data_source.infrastructure.bsc.pancakeswap_tokens_data_source import (
    PancakeswapToken,
    PancakeswapTokenListDataSource,
    Response,
)


@fixture
def id_generator():
    return mock.Mock(spec=IdGenerator)


@fixture
def http_request():
    return mock.Mock(spec=HttpRequest)


@mark.asyncio
async def test_pancakeswap_tokens_data_source_get(
    snapshot, http_request: HttpRequest, id_generator: IdGenerator
):
    http_request.get = mock.AsyncMock(
        return_value=Response(
            tokens=[
                PancakeswapToken(
                    chainId=56,
                    address="0x61909950e1bfb5d567c5463cbd33dc1cdc85ee93",
                    name="Lithosphere",
                    symbol="LITHO",
                    decimals=18,
                    logoURI="https://tokens.pancakeswap.finance/images/0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82.png",
                )
            ]
        )
    )

    id_generator.generate_id.return_value = "d179fa30-808d-48a9-98f3-93c8702e78d8"

    # Create an instance of the data source with the mocked HttpRequest
    data_source = PancakeswapTokenListDataSource(http_request, id_generator)

    # Call the get method and check the result
    similarity_documents = await data_source.get()

    assert similarity_documents == snapshot

    http_request.get.assert_called_once_with(
        {
            "url": "https://tokens.pancakeswap.finance/pancakeswap-extended.json",
            "headers": {
                "accept": "application/json",
            },
        },
        Response,
    )


def test_pancakeswap_tokens_data_source_version(
    http_request: HttpRequest,
    id_generator: IdGenerator,
):
    data_source = PancakeswapTokenListDataSource(http_request, id_generator)
    version = data_source.version()

    assert version == 3


@mark.asyncio
async def test_pancakeswap_tokens_data_source_display_name_cleaning(
    http_request: HttpRequest, id_generator: IdGenerator
):
    http_request.get = mock.AsyncMock(
        return_value=Response(
            tokens=[
                PancakeswapToken(
                    chainId=56,
                    address="0x1234567890abcdef1234567890abcdef12345678",
                    name="Binance Pegged Wrapped Bitcoin",
                    symbol="BTCB",
                    decimals=18,
                    logoURI="https://assets.coingecko.com/coins/images/1/thumb/bitcoin.png",
                ),
                PancakeswapToken(
                    chainId=56,
                    address="0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
                    name="Wrapped Ethereum",
                    symbol="WETH",
                    decimals=18,
                    logoURI="https://assets.coingecko.com/coins/images/279/thumb/ethereum.png",
                ),
                PancakeswapToken(
                    chainId=56,
                    address="0x1111111111111111111111111111111111111111",
                    name="Binance Pegged USD Coin",
                    symbol="USDC",
                    decimals=18,
                    logoURI="https://assets.coingecko.com/coins/images/6319/thumb/USD_Coin_icon.png",
                ),
                PancakeswapToken(
                    chainId=56,
                    address="0x2222222222222222222222222222222222222222",
                    name="Tether",
                    symbol="USDT",
                    decimals=18,
                    logoURI="https://assets.coingecko.com/coins/images/325/thumb/Tether.png",
                ),
            ]
        )
    )
    id_generator.generate_id.side_effect = ["id1", "id2", "id3", "id4"]

    data_source = PancakeswapTokenListDataSource(http_request, id_generator)
    similarity_documents = await data_source.get()

    assert similarity_documents[0].metadata["source"]["display_name"] == "Bitcoin"
    assert similarity_documents[1].metadata["source"]["display_name"] == "Ethereum"
    assert similarity_documents[2].metadata["source"]["display_name"] == "USD Coin"
    assert similarity_documents[3].metadata["source"]["display_name"] == "Tether"
