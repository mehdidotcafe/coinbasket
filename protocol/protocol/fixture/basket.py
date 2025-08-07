from decimal import Decimal
from protocol.basket import Basket
from protocol.fixture.token import btc_token, wbnb_token, eth_token, sol_token
from protocol.token import Token

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

memecoinmania_basket = Basket(
    id="c0e724d3-c4d0-4bd0-973d-edd3907ecf51",
    name="Memecoin Mania",
    description="A basket of popular memecoins",
    denomination=Decimal("1"),
    tokens=[
        Token(
            id="bsc:0xbA2aE424d960c26247Dd6c32edC70B295c744C43",
            name="Dogecoin",
            display_name="Dogecoin",
            ticker="DOGE",
            address="0xbA2aE424d960c26247Dd6c32edC70B295c744C43",
        ),
        Token(
            id="bsc:0x2859e4544C4bB03966803b044A93563Bd2D0DD4D",
            name="SHIBA INU",
            display_name="Shiba Inu",
            ticker="SHIB",
            address="0x2859e4544C4bB03966803b044A93563Bd2D0DD4D",
        ),
        Token(
            id="bsc:0x25d887Ce7a35172C62FeBFD67a1856F20FaEbB00",
            name="Pepe",
            display_name="Pepe",
            ticker="PEPE",
            address="0x25d887Ce7a35172C62FeBFD67a1856F20FaEbB00",
        ),
        Token(
            id="bsc:0xfb5b838b6cfeedc2873ab27866079ac55363d37e",
            name="FLOKI",
            display_name="FLOKI",
            ticker="FLOKI",
            address="0xfb5b838b6cfeedc2873ab27866079ac55363d37e",
        ),
        Token(
            id="bsc:0xA697e272a73744b343528C3Bc4702F2565b2F422",
            name="Bonk",
            display_name="Bonk",
            ticker="BONK",
            address="0xA697e272a73744b343528C3Bc4702F2565b2F422",
        ),
        Token(
            id="bsc:0x86Bb94DdD16Efc8bc58e6b056e8df71D9e666429",
            name="Test",
            display_name="Test",
            ticker="TST",
            address="0x86Bb94DdD16Efc8bc58e6b056e8df71D9e666429",
        ),
        Token(
            id="bsc:0x5C85D6C6825aB4032337F11Ee92a72DF936b46F6",
            name="mubarak",
            display_name="mubarak",
            ticker="MUBARAK",
            address="0x5C85D6C6825aB4032337F11Ee92a72DF936b46F6",
        ),
    ],
)
