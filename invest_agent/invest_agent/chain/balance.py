from dataclasses import dataclass
from decimal import Decimal
import json
from typing import Any, Generic, TypeVar

from protocol.asset import Asset
from protocol.basket import Basket
from protocol.token import Token

T = TypeVar("T", bound=Asset, default=Asset, covariant=True)

AmountReadable = Decimal
AmountAtomic = int


@dataclass
class Balance(Generic[T]):
    asset: T
    amount: AmountReadable

    def serialize(self):
        """Serialize a balance to JSON."""
        return json.dumps(
            {
                "asset": self.asset.to_dict(),
                "amount": format(self.amount, "f"),
            }
        )

    @staticmethod
    def deserialize(balance_as_str: str):
        """Deserialize a balance from JSON as string."""
        balance_as_json = json.loads(balance_as_str)

        def deserialize_token(token: dict[str, Any]) -> Token:
            return Token(
                id=token["id"],
                name=token["name"],
                display_name=token["display_name"],
                ticker=token["ticker"],
                address=token["address"],
            )

        asset = (
            Basket(
                id=balance_as_json["asset"]["id"],
                name=balance_as_json["asset"]["name"],
                display_name=balance_as_json["asset"]["display_name"],
                ticker=balance_as_json["asset"]["ticker"],
                description=balance_as_json["asset"]["description"],
                denomination=Decimal(balance_as_json["asset"]["denomination"]),
                tokens=[
                    deserialize_token(token)
                    for token in balance_as_json["asset"]["tokens"]
                ],
            )
            if "tokens" in balance_as_json["asset"]
            else deserialize_token(balance_as_json["asset"])
        )

        return Balance(
            asset=asset,
            amount=Decimal(balance_as_json["amount"]),
        )


@dataclass
class BalanceAtomic(Balance, Generic[T]):
    asset: T
    amount: AmountReadable
    amount_atomic: AmountAtomic
    decimals: int

    def serialize(self):
        """Serialize a balance to JSON."""
        return json.dumps(
            {
                "asset": self.asset.to_dict(),
                "amount": format(self.amount, "f"),
                "amount_atomic": self.amount_atomic,
                "decimals": self.decimals,
            }
        )

    @staticmethod
    def deserialize(balance_as_str: str):
        """Deserialize a balance from JSON as string."""
        balance_as_json = json.loads(balance_as_str)

        def deserialize_token(token: dict[str, Any]) -> Token:
            return Token(
                id=token["id"],
                name=token["name"],
                display_name=token["display_name"],
                ticker=token["ticker"],
                address=token["address"],
            )

        asset = (
            Basket(
                id=balance_as_json["asset"]["id"],
                name=balance_as_json["asset"]["name"],
                display_name=balance_as_json["asset"]["display_name"],
                ticker=balance_as_json["asset"]["ticker"],
                description=balance_as_json["asset"]["description"],
                denomination=Decimal(balance_as_json["asset"]["denomination"]),
                tokens=[
                    deserialize_token(token)
                    for token in balance_as_json["asset"]["tokens"]
                ],
            )
            if "tokens" in balance_as_json["asset"]
            else deserialize_token(balance_as_json["asset"])
        )

        return BalanceAtomic(
            asset=asset,
            amount=Decimal(balance_as_json["amount"]),
            amount_atomic=balance_as_json["amount_atomic"],
            decimals=balance_as_json["decimals"],
        )

    @staticmethod
    def deserialize_asset(asset_as_str: str) -> Asset:
        """Deserialize an asset from JSON as string."""
        asset_as_json = json.loads(asset_as_str)

        def deserialize_token(token: dict[str, Any]) -> Token:
            return Token(
                id=token["id"],
                name=token["name"],
                display_name=token["display_name"],
                ticker=token["ticker"],
                address=token["address"],
            )

        if "tokens" in asset_as_json:
            return Basket(
                id=asset_as_json["id"],
                name=asset_as_json["name"],
                display_name=asset_as_json["display_name"],
                ticker=asset_as_json["ticker"],
                description=asset_as_json["description"],
                denomination=Decimal(asset_as_json["denomination"]),
                tokens=[deserialize_token(token) for token in asset_as_json["tokens"]],
            )
        return deserialize_token(asset_as_json)

    def __add_decimal(self, amount_atomic: Decimal) -> "BalanceAtomic[T]":
        amount_atomic = self.amount_atomic + amount_atomic
        amount = Decimal(amount_atomic) / (10**self.decimals)

        return BalanceAtomic(
            asset=self.asset,
            amount=amount,
            amount_atomic=int(amount_atomic),
            decimals=self.decimals,
        )

    def __add__(self, other: "BalanceAtomic[T] | Decimal") -> "BalanceAtomic[T]":
        if isinstance(other, Decimal):
            return self.__add_decimal(other)

        if self.asset.id != other.asset.id:
            raise ValueError("Cannot add balances with different assets")

        amount_atomic = self.amount_atomic + other.amount_atomic
        amount = Decimal(amount_atomic) / (10**self.decimals)

        return BalanceAtomic(
            asset=self.asset,
            amount=amount,
            amount_atomic=amount_atomic,
            decimals=self.decimals,
        )

    def __sub_decimal(self, amount_atomic: Decimal) -> "BalanceAtomic[T]":
        amount_atomic = self.amount_atomic - amount_atomic
        amount = Decimal(amount_atomic) / (10**self.decimals)

        return BalanceAtomic(
            asset=self.asset,
            amount=amount,
            amount_atomic=int(amount_atomic),
            decimals=self.decimals,
        )

    def __sub__(self, other: "BalanceAtomic[T] | Decimal") -> "BalanceAtomic[T]":
        if isinstance(other, Decimal):
            return self.__sub_decimal(other)

        if self.asset.id != other.asset.id:
            raise ValueError("Cannot subtract balances with different assets")

        amount_atomic = self.amount_atomic - other.amount_atomic
        amount = Decimal(amount_atomic) / (10**self.decimals)

        return BalanceAtomic(
            asset=self.asset,
            amount=amount,
            amount_atomic=amount_atomic,
            decimals=self.decimals,
        )

    def __mul_decimal(self, factor: Decimal) -> "BalanceAtomic[T]":
        amount_atomic = int(self.amount_atomic * factor)
        amount = Decimal(amount_atomic) / (10**self.decimals)

        return BalanceAtomic(
            asset=self.asset,
            amount=amount,
            amount_atomic=amount_atomic,
            decimals=self.decimals,
        )

    def __mul__(self, other: "BalanceAtomic[T] | Decimal") -> "BalanceAtomic[T]":
        if isinstance(other, Decimal):
            return self.__mul_decimal(other)

        if self.asset.id != other.asset.id:
            raise ValueError("Cannot multiply balances with different assets")

        amount_atomic = int(self.amount_atomic * other.amount_atomic)
        amount = Decimal(amount_atomic) / (10**self.decimals)

        return BalanceAtomic(
            asset=self.asset,
            amount=amount,
            amount_atomic=amount_atomic,
            decimals=self.decimals,
        )

    def __div_decimal(self, divisor: Decimal) -> "BalanceAtomic[T]":
        amount_atomic = int(self.amount_atomic / divisor)
        amount = Decimal(amount_atomic) / (10**self.decimals)

        return BalanceAtomic(
            asset=self.asset,
            amount=amount,
            amount_atomic=amount_atomic,
            decimals=self.decimals,
        )

    def __truediv__(self, other: "BalanceAtomic[T] | Decimal") -> "BalanceAtomic[T]":
        if isinstance(other, Decimal):
            return self.__div_decimal(other)

        if self.asset.id != other.asset.id:
            raise ValueError("Cannot divide balances with different assets")

        amount_atomic = int(self.amount_atomic / other.amount_atomic)
        amount = Decimal(amount_atomic) / (10**self.decimals)

        return BalanceAtomic(
            asset=self.asset,
            amount=amount,
            amount_atomic=amount_atomic,
            decimals=self.decimals,
        )
