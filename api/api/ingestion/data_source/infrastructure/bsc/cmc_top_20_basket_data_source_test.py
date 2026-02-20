from unittest import mock
from api.ingestion.data_source.infrastructure.bsc.cmc_top_20_basket_data_source import (
    CmcTop20BasketDataSource,
)
from api.shared.id_generator.id_generator import IdGenerator
from pytest import fixture, mark


@fixture
def id_generator():
    id_generator = mock.Mock(spec=IdGenerator)

    id_generator.generate_id.side_effect = lambda x: f"generated-id-{x}"

    return id_generator


@mark.asyncio
async def test_cmc_top_20_basket_data_source_get(snapshot, id_generator: IdGenerator):
    data_source = CmcTop20BasketDataSource(id_generator)
    data = await data_source.get()

    assert data == snapshot


def test_cmc_top_20_basket_data_source_version(id_generator: IdGenerator):
    data_source = CmcTop20BasketDataSource(id_generator)
    version = data_source.version()

    assert version == 2
