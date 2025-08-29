from pytest import mark
from data_agent.ingestion.data_source.infrastructure.bsc.cmc_top_10_2025 import (
    CmcTop102025BasketDataSource,
)


@mark.asyncio
async def test_cmc_top_10_2025_basket_data_source_get(snapshot):
    data_source = CmcTop102025BasketDataSource()
    data = await data_source.get()

    assert data == snapshot


def test_cmc_top_10_2025_basket_data_source_version():
    data_source = CmcTop102025BasketDataSource()
    version = data_source.version()

    assert version == 2
