from api.protocol.token import Token


def test_token_eq_true() -> None:
    token1 = Token(
        id="token-1",
        name="Token One",
        display_name="Token One",
        ticker="TKN1",
        address="0x123",
        description="First test token",
        decimals=18,
        categories=[],
    )
    token2 = Token(
        id="token-1",
        name="Token One",
        display_name="Token One",
        ticker="TKN1",
        address="0x123",
        description="First test token",
        decimals=18,
        categories=[],
    )
    assert token1 == token2


def test_token_eq_false() -> None:
    token1 = Token(
        id="token-1",
        name="Token One",
        display_name="Token One",
        ticker="TKN1",
        address="0x123",
        description="First test token",
        decimals=18,
        categories=[],
    )
    token2 = Token(
        id="token-2",
        name="Token Two",
        display_name="Token Two",
        ticker="TKN2",
        address="0x456",
        description="Second test token",
        decimals=6,
        categories=[],
    )
    assert token1 != token2


def test_token_eq_non_token() -> None:
    token = Token(
        id="token-1",
        name="Token One",
        display_name="Token One",
        ticker="TKN1",
        address="0x123",
        description="Test token",
        decimals=18,
        categories=[],
    )
    assert token != "not a token"
