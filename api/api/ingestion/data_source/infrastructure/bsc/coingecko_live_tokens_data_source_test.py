from unittest import mock
from api.token.infrastructure.coingecko.coingecko_token_repository import (
    CoingeckoTokenRepository,
)
from pytest import fixture, mark
from typing import Any

from api.shared.id_generator.id_generator import IdGenerator
from api.ingestion.data_source.infrastructure.bsc.coingecko_live_tokens_data_source import (
    CoingeckoLiveTokenListDataSource,
)
from api.protocol.fixture.token import sol_token, usdt_token, eth_token


@fixture
def id_generator():
    return mock.Mock(spec=IdGenerator)


@fixture
def token_repository():
    return mock.Mock(spec=CoingeckoTokenRepository)


@mark.asyncio
async def test_coingecko_live_tokens_data_source_get(
    snapshot: Any,
    token_repository: CoingeckoTokenRepository,
    id_generator: IdGenerator,
):
    id_generator.generate_id.side_effect = lambda x: f"generated-id-{x}"

    token_repository.get_all_tokens.return_value = [sol_token, usdt_token, eth_token]
    token_repository.get_by_address.side_effect = [sol_token, usdt_token, eth_token]

    data_source = CoingeckoLiveTokenListDataSource(
        id_generator=id_generator,
        token_repository=token_repository,
    )
    data = await data_source.get()

    assert data == snapshot


def test_coingecko_live_tokens_data_source_version(
    token_repository: CoingeckoTokenRepository,
    id_generator: IdGenerator,
):
    data_source = CoingeckoLiveTokenListDataSource(
        id_generator=id_generator,
        token_repository=token_repository,
    )
    version = data_source.version()

    assert version == 5
