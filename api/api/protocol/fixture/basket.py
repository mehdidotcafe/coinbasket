from decimal import Decimal
from api.protocol.basket import Basket
from api.protocol.fixture.token import (
    btc_token,
    wbnb_token,
    eth_token,
    sol_token,
    doge_token,
    shib_token,
    pepe_token,
)

test_basket = Basket(
    id="0d83917d-a2bd-4482-83e6-68d52c8f293a",
    name="Test Basket",
    display_name="Test Basket",
    ticker="TEST",
    description="A basket for testing purposes",
    denomination=Decimal("10.0"),
    tokens=[
        btc_token,
        eth_token,
    ],
)

big4_basket = Basket(
    id="2bb6425b-a9ee-4292-89c8-c1f0c7a5cb70",
    name="Big4",
    display_name="Big4",
    ticker="B4",
    description="This curated basket offers broad exposure to the crypto market through a selection of established, high-liquidity digital assets spanning different blockchain ecosystems. It is designed to balance long-term value preservation with growth potential, reflecting both foundational and emerging trends in decentralized technology. The combination supports diversification across transaction layers, use cases, and network adoption, making it a resilient core holding for crypto-oriented portfolios.",
    denomination=Decimal("10.0"),
    tokens=[
        btc_token,
        eth_token,
        sol_token,
        wbnb_token,
    ],
)

memecoinmania_basket = Basket(
    id="c0e724d3-c4d0-4bd0-973d-edd3907ecf51",
    name="Memecoin Mania",
    display_name="Memecoin Mania",
    ticker="MEME",
    description="A basket of popular memecoins",
    denomination=Decimal("1"),
    tokens=[
        doge_token,
        shib_token,
        pepe_token,
    ],
)
