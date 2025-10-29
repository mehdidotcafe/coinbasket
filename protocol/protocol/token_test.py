from protocol.token import Token


def test_token_eq_true() -> None:
    token1 = Token(
        id="token-1",
        name="Token One",
        display_name="Token One",
        ticker="TKN1",
        address="0x123",
    )
    token2 = Token(
        id="token-1",
        name="Token One",
        display_name="Token One",
        ticker="TKN1",
        address="0x123",
    )
    assert token1 == token2


def test_token_eq_false() -> None:
    token1 = Token(
        id="token-1",
        name="Token One",
        display_name="Token One",
        ticker="TKN1",
        address="0x123",
    )
    token2 = Token(
        id="token-2",
        name="Token Two",
        display_name="Token Two",
        ticker="TKN2",
        address="0x456",
    )
    assert token1 != token2


def test_token_eq_non_token() -> None:
    token = Token(
        id="token-1",
        name="Token One",
        display_name="Token One",
        ticker="TKN1",
        address="0x123",
    )
    assert token != "not a token"


def test_token__str__():
    token = Token(
        id="1234",
        name="Wrapped BNB",
        display_name="Wrapped BNB",
        ticker="WBNB",
        address="0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7",
    )

    assert (
        str(token)
        == """
name: Wrapped BNB
display_name: Wrapped BNB
ticker: WBNB
address: 0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7
type: token
"""
    )
