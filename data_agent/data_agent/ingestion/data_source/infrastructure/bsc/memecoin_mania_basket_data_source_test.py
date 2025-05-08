from data_agent.ingestion.data_source.infrastructure.bsc.memecoin_mania_basket_data_source import (
    MemecoinManiaBasketDataSource,
)


def test_memecoin_mania_basket_data_source_get(snapshot):
    data_source = MemecoinManiaBasketDataSource()
    data = data_source.get()

    assert data == snapshot


def test_memecoin_mania_basket_data_source_version():
    data_source = MemecoinManiaBasketDataSource()
    version = data_source.version()

    assert version == 1
