from data_agent.ingestion.data_source.infrastructure.bsc.memecoin_mania_basket_data_source import (
    MemecoinManiaBasketDataSource,
)
from pytest import mark


@mark.asyncio
async def test_memecoin_mania_basket_data_source_get(snapshot):
    data_source = MemecoinManiaBasketDataSource()
    data = await data_source.get()

    assert data == snapshot


def test_memecoin_mania_basket_data_source_version():
    data_source = MemecoinManiaBasketDataSource()
    version = data_source.version()

    assert version == 2
