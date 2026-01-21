from api.similarity.asset_similarity import BasketSimilarity, TokenSimilarity


def test_token_similarity_to_document():
    token = TokenSimilarity(
        id="bsc:0x1234567890abcdef",
        name="Bitcoin",
        display_name="Bitcoin",
        description="A decentralized digital currency.",
        ticker="BTC",
        address="0x1234567890abcdef",
        categories=["Action Games", "Analytics"],
        is_canonical=1,
        market_cap_usd=800000000000,
        trust_score=10,
        decimals=18,
    )

    expected_document = """
name: Bitcoin
display_name: Bitcoin
description: A decentralized digital currency.
ticker: BTC
address: 0x1234567890abcdef
categories: Action Games, Analytics
"""

    assert token.to_document() == expected_document


def test_basket_similarity_to_document():
    basket = BasketSimilarity(
        id="bsc:0x1234567890abcdef",
        name="DeFi Basket",
        display_name="DeFi Basket",
        description="A basket of top DeFi tokens.",
        ticker="DEFI",
        address="0xabcdef1234567890",
        categories=["DeFi", "Finance"],
        is_canonical=1,
        market_cap_usd=5000000000,
        trust_score=85,
        decimals=18,
    )

    expected_document = """
name: DeFi Basket
display_name: DeFi Basket
description: A basket of top DeFi tokens.
ticker: DEFI
address: 0xabcdef1234567890
categories: DeFi, Finance
"""
    assert basket.to_document() == expected_document
