from decimal import Decimal
from protocol.basket import Basket
from protocol.token import Token


def test_basket__str__():
    basket = Basket(
        id="1234",
        name="Big2",
        description="Big2",
        unit=Decimal("1.0"),
        tokens=[
            Token(
                id="456",
                name="Binance Pegged Bitcoin",
                display_name="Bitcoin",
                ticker="BTC",
                address="0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
            ),
            Token(
                id="789",
                name="Binance Pegged Ethereum",
                display_name="Ethereum",
                ticker="ETH",
                address="0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
            ),
        ],
    )

    assert (
        str(basket)
        == """
name: Big2
description: Big2
type: basket
1. name: Binance Pegged Bitcoin
 display_name: Bitcoin
 ticker: BTC
 address: 0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c

2. name: Binance Pegged Ethereum
 display_name: Ethereum
 ticker: ETH
 address: 0x2170Ed0880ac9A755fd29B2688956BD959F933F8

"""
    )
