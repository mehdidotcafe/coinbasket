from typing import Literal


class Basket:
    id: str
    name: str
    display_name: str
    description: str
    ticker: str
    decimals: int
    address: str
    categories: list[str]
    logo_uri: str | None = None
    type: Literal["BASKET"]

    def __init__(
        self,
        id: str,
        name: str,
        display_name: str,
        ticker: str,
        address: str,
        description: str,
        decimals: int,
        categories: list[str],
        logo_uri: str | None = None,
    ):
        self.id = id.lower()
        self.name = name
        self.display_name = display_name
        self.ticker = ticker
        self.address = address
        self.description = description
        self.decimals = decimals
        self.categories = categories
        self.logo_uri = logo_uri
        self.type = "BASKET"

    def __str__(self) -> str:
        return f"""
name: {self.name}
display_name: {self.display_name}
description: {self.description}
ticker: {self.ticker}
decimals: {self.decimals}
address: {self.address}
logo_uri: {self.logo_uri or ""}
categories: {", ".join(self.categories)}
type: {self.type.lower()}
"""

    def to_dict(self) -> dict[str, str | int | list[str] | None]:
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "ticker": self.ticker,
            "address": self.address,
            "description": self.description,
            "decimals": int(self.decimals),
            "logo_uri": self.logo_uri,
            "categories": self.categories,
            "type": self.type,
        }

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Basket):
            return False
        return self.id == value.id
