from dataclasses import dataclass


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
