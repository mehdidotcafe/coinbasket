from data_agent.ingestion.data_source.infrastructure.bsc.cryptoummah_halal_basket_data_source import (
    CryptoUmmahHalalBasketDataSource,
)
from pytest import mark


@mark.asyncio
async def test_crypto_ummah_halal_basket_data_source_get(snapshot):
    data_source = CryptoUmmahHalalBasketDataSource()
    data = await data_source.get()

    assert data == snapshot


def test_crypto_ummah_halal_basket_data_source_version():
    data_source = CryptoUmmahHalalBasketDataSource()
    version = data_source.version()

    assert version == 3
