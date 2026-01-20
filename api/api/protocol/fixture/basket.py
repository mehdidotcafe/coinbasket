from api.protocol.basket import Basket

test_basket = Basket(
    id="0d83917d-a2bd-4482-83e6-68d52c8f293a",
    name="Test Basket",
    display_name="Test Basket",
    ticker="TEST",
    description="A basket for testing purposes",
    decimals=18,
    address="0x0000000000000000000000000000000000000000",
    categories=["test", "demo"],
)

cmc20_basket = Basket(
    id="0x2f8A339B5889FfaC4c5A956787cdA593b3c36867",
    name="CMC20 Basket",
    display_name="CMC20 Basket",
    ticker="CMC20",
    description="Top 20 tokens by market cap",
    decimals=18,
    address="0x2f8A339B5889FfaC4c5A956787cdA593b3c36867",
    categories=["market-cap", "diversified"],
)
