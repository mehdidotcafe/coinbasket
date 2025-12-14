from api.ingestion.data_source.infrastructure.bsc.ai_basket_data_source import (
    AiBasketDataSource,
)
from pytest import mark


@mark.asyncio
async def test_ai_basket_data_source_get(snapshot):
    data_source = AiBasketDataSource()
    data = await data_source.get()

    assert data == snapshot


def test_ai_basket_data_source_version():
    data_source = AiBasketDataSource()
    version = data_source.version()

    assert version == 3
