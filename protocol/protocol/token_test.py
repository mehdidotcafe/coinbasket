from protocol.token import Token


def test_token__str__():
    token = Token(
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
"""
    )
