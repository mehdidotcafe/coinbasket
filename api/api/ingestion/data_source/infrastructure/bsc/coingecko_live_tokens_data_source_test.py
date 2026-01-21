from unittest import mock
from api.similarity.trust_scorer.asset_trust_scorer_strategy import (
    AssetTrustScorerStrategy,
)
from api.token.infrastructure.coingecko.coingecko_token_repository import (
    CoingeckoTokenRepository,
)
from pydantic import BaseModel
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


@fixture
def asset_trust_scorer_strategy():
    scorer = mock.Mock(spec=AssetTrustScorerStrategy)

    scorer.score.side_effect = [80, 50, 10]
    return scorer


@mark.asyncio
async def test_coingecko_live_tokens_data_source_get(
    snapshot: Any,
    token_repository: CoingeckoTokenRepository,
    id_generator: IdGenerator,
    asset_trust_scorer_strategy: AssetTrustScorerStrategy,
):
    id_generator.generate_id.side_effect = lambda x: f"generated-id-{x}"

    sol_token_model = mock.Mock(spec=BaseModel)
    sol_token_model.model_dump.return_value = {"address": "0xsol_token_address"}

    usdt_token_model = mock.Mock(spec=BaseModel)
    usdt_token_model.model_dump.return_value = {"address": "0xusdt_token_address"}

    eth_token_model = mock.Mock(spec=BaseModel)
    eth_token_model.model_dump.return_value = {"address": "0xeth_token_address"}

    token_repository.get_all_tokens.return_value = [sol_token, usdt_token, eth_token]
    token_repository.get_by_address.side_effect = [
        (sol_token, sol_token_model),
        (usdt_token, usdt_token_model),
        (eth_token, eth_token_model),
    ]

    data_source = CoingeckoLiveTokenListDataSource(
        id_generator=id_generator,
        token_repository=token_repository,
        asset_trust_scorer_strategy=asset_trust_scorer_strategy,
    )
    data = await data_source.get()

    assert data == snapshot

    asset_trust_scorer_strategy.score.assert_has_calls(
        [
            mock.call({"address": "0xsol_token_address"}),
            mock.call({"address": "0xusdt_token_address"}),
            mock.call({"address": "0xeth_token_address"}),
        ]
    )


def test_coingecko_live_tokens_data_source_version(
    token_repository: CoingeckoTokenRepository,
    id_generator: IdGenerator,
    asset_trust_scorer_strategy: AssetTrustScorerStrategy,
):
    data_source = CoingeckoLiveTokenListDataSource(
        id_generator=id_generator,
        token_repository=token_repository,
        asset_trust_scorer_strategy=asset_trust_scorer_strategy,
    )
    version = data_source.version()

    assert version == 7
