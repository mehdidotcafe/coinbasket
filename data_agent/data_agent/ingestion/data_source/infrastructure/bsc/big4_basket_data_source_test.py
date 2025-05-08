from data_agent.ingestion.data_source.infrastructure.bsc.big4_basket_data_source import (
    Big4BasketDataSource,
)


def test_big4_basket_data_source_get(snapshot):
    data_source = Big4BasketDataSource()
    data = data_source.get()

    assert data == snapshot


def test_big4_basket_data_source_version():
    data_source = Big4BasketDataSource()
    version = data_source.version()

    assert version == 1
