from data_agent.ingestion.data_source.infrastructure.bsc.cmc_top_10_2025 import (
    CmcTop102025BasketDataSource,
)


def test_cmc_top_10_2025_basket_data_source_get(snapshot):
    data_source = CmcTop102025BasketDataSource()
    data = data_source.get()

    assert data == snapshot


def test_cmc_top_10_2025_basket_data_source_version():
    data_source = CmcTop102025BasketDataSource()
    version = data_source.version()

    assert version == 1
