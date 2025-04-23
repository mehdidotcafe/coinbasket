from pytest import fixture
from coinbasket.chain.bsc_chain import BscChain


@fixture
def bsc_chain():
    return BscChain(
        rpc_url="https://bsc-dataseed.binance.org/",
        private_key="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
    )


def test_defined(bsc_chain: BscChain):
    assert bsc_chain is not None


def test_get_min_balance(bsc_chain: BscChain):
    min_balance = bsc_chain.get_min_balance()

    assert min_balance.amount == 0.035
    assert min_balance.currency == "BNB"
