from api.protocol.basket import Basket


def test_basket__str__():
    basket = Basket(
        id="1234",
        name="Big2",
        display_name="Big2 Display",
        ticker="B2",
        description="Big2 Description",
        address="0xbasketaddress1234",
        decimals=18,
        categories=["8Bit Chain Ecosystem", "8Bit Chain Ecosystem"],
        logo_uri=None,
    )

    assert (
        str(basket)
        == """
name: Big2
display_name: Big2 Display
description: Big2 Description
ticker: B2
address: 0xbasketaddress1234
categories: 8Bit Chain Ecosystem, 8Bit Chain Ecosystem
"""
    )
