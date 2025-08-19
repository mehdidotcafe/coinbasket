from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Token:
    id: str
    name: str
    display_name: str
    ticker: str
    address: str

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
