from unittest import mock
from pytest import fixture, mark
from typing import Any

from data_agent.ingestion.id.id_generator import IdGenerator
from shared.http_request.http_request import HttpRequest
from data_agent.ingestion.data_source.infrastructure.bsc.coingecko_live_tokens_data_source import (
    CoingeckoLiveTokenListDataSource,
    CoinListToken,
    CoinListResponse,
    Configuration,
)


@fixture
def id_generator():
    return mock.Mock(spec=IdGenerator)


@fixture
def http_request():
    return mock.Mock(spec=HttpRequest)


@mark.asyncio
async def test_coingecko_live_tokens_data_source_get(
    snapshot: Any,
    http_request: HttpRequest,
    id_generator: IdGenerator,
):
    coin_list_response = CoinListResponse(
        tokens=[
            CoinListToken(
                chainId=56,
                address="0x61909950e1bfb5d567c5463cbd33dc1cdc85ee93",
                name="Lithosphere",
                symbol="litho",
                decimals=18,
                logoURI="",
            )
        ]
    )

    http_request.get.return_value = coin_list_response
    id_generator.generate_id = mock.Mock(
        return_value="d179fa30-808d-48a9-98f3-93c8702e78d8"
    )

    cfg: Configuration = {
        "coingecko_base_url": "configuration.coingecko_base_url",
        "coingecko_api_key": "configuration.coingecko_api_key",
    }
    data_source = CoingeckoLiveTokenListDataSource(http_request, id_generator, cfg)

    similarity_documents = await data_source.get()
    assert similarity_documents == snapshot

    list_call_args = http_request.get.call_args_list[0][0][0]
    assert list_call_args["url"].endswith(
        "/v3/token_lists/binance-smart-chain/all.json"
    )

    assert "x-cg-demo-api-key" in list_call_args["headers"]


def test_coingecko_live_tokens_data_source_version(
    http_request: HttpRequest, id_generator: IdGenerator
):
    cfg: Configuration = {
        "coingecko_base_url": "configuration.coingecko_base_url,",
        "coingecko_api_key": "configuration.coingecko_api_key,",
    }
    data_source = CoingeckoLiveTokenListDataSource(http_request, id_generator, cfg)
    assert data_source.version() == 4
