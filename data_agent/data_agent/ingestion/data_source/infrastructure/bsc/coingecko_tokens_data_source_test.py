from unittest import mock
from pytest import fixture, mark
from data_agent.ingestion.id.id_generator import IdGenerator
from shared.http_request.http_request import HttpRequest
from data_agent.ingestion.data_source.infrastructure.bsc.coingecko_tokens_data_source import (
    CoingeckoToken,
    CoingeckoTokenListDataSource,
    Response,
)


@fixture
def id_generator():
    return mock.Mock(spec=IdGenerator)


@fixture
def http_request():
    return mock.Mock(spec=HttpRequest)


@mark.asyncio
async def test_coingecko_tokens_data_source_get(
    snapshot, http_request: HttpRequest, id_generator: IdGenerator
):
    http_request.get = mock.AsyncMock(
        return_value=Response(
            tokens=[
                CoingeckoToken(
                    chainId=56,
                    address="0x61909950e1bfb5d567c5463cbd33dc1cdc85ee93",
                    name="Lithosphere",
                    symbol="LITHO",
                    decimals=18,
                    logoURI="https://assets.coingecko.com/coins/images/21128/thumb/6gizpBLn.png?1696520507",
                )
            ]
        )
    )
    id_generator.generate_id.return_value = "d179fa30-808d-48a9-98f3-93c8702e78d8"

    # Create an instance of the data source with the mocked HttpRequest
    data_source = CoingeckoTokenListDataSource(http_request, id_generator)

    # Call the get method and check the result
    similarity_documents = await data_source.get()

    assert similarity_documents == snapshot

    http_request.get.assert_called_once_with(
        {
            "url": "https://tokens.coingecko.com/binance-smart-chain/all.json",
            "headers": {
                "accept": "application/json",
            },
        },
        Response,
    )


def test_coingecko_tokens_data_source_version(
    http_request: HttpRequest,
    id_generator: IdGenerator,
):
    data_source = CoingeckoTokenListDataSource(http_request, id_generator)
    version = data_source.version()

    assert version == 2
