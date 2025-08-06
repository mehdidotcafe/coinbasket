from decimal import Decimal
from protocol.basket import Basket
from protocol.fixture.token import btc_token, wbnb_token, eth_token, sol_token

big4_basket = Basket(
    id="2bb6425b-a9ee-4292-89c8-c1f0c7a5cb70",
    name="Big4",
    description="This curated basket offers broad exposure to the crypto market through a selection of established, high-liquidity digital assets spanning different blockchain ecosystems. It is designed to balance long-term value preservation with growth potential, reflecting both foundational and emerging trends in decentralized technology. The combination supports diversification across transaction layers, use cases, and network adoption, making it a resilient core holding for crypto-oriented portfolios.",
    denomination=Decimal("10.0"),
    tokens=[
        btc_token,
        eth_token,
        sol_token,
        wbnb_token,
    ],
)
