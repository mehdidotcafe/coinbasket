from data_agent.ingestion.data_source.infrastructure.bsc.ai_basket_data_source import (
    AiBasketDataSource,
)


def test_ai_basket_data_source_get(snapshot):
    data_source = AiBasketDataSource()
    data = data_source.get()

    assert data == snapshot


def test_ai_basket_data_source_version():
    data_source = AiBasketDataSource()
    version = data_source.version()

    assert version == 1
