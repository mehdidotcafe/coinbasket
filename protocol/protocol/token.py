from decimal import Decimal


class Token:
    id: str
    name: str
    display_name: str
    ticker: str
    address: str

    def __init__(
        self, id: str, name: str, display_name: str, ticker: str, address: str
    ):
        self.id = id.lower()
        self.name = name
        self.display_name = display_name
        self.ticker = ticker
        self.address = address

    def __str__(self) -> str:
        return f"""
name: {self.name}
display_name: {self.display_name}
ticker: {self.ticker}
address: {self.address}
type: token
"""

    def to_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "ticker": self.ticker,
            "address": self.address,
        }

    def get_pricing_token(self) -> "Token":
        return self

    def get_denomination(self) -> Decimal:
        return Decimal("1")

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Token):
            return False
        return self.id == value.id
