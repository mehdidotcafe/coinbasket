from dataclasses import dataclass
from decimal import Decimal
import json
from typing import Any, Generic, TypeVar

from api.protocol.asset import Asset
from api.protocol.basket import Basket
from api.protocol.token import Token

T = TypeVar("T", bound=Asset, default=Asset, covariant=True)

AmountReadable = Decimal
AmountAtomic = int


@dataclass
class Balance(Generic[T]):
    asset: T
    amount: AmountReadable

    def serialize(self):
        """Serialize a balance to JSON."""
        return json.dumps(self.to_dict())

    @staticmethod
    def deserialize(balance_as_str: str):
        """Deserialize a balance from JSON as string."""
        balance_as_json = json.loads(balance_as_str)

        def deserialize_asset(asset: dict[str, Any]) -> Asset:
            ChildAsset = Token if asset["type"] == "TOKEN" else Basket

            return ChildAsset(
                id=asset["id"],
                name=asset["name"],
                display_name=asset["display_name"],
                ticker=asset["ticker"],
                address=asset["address"],
                decimals=asset["decimals"],
                categories=asset["categories"],
                description=asset["description"],
            )

        asset = deserialize_asset(balance_as_json["asset"])

        return Balance(
            asset=asset,
            amount=Decimal(balance_as_json["amount"]),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the Balance to a dictionary."""
        return {
            "asset": self.asset.to_dict(),
            "amount": format(self.amount, "f"),
        }


@dataclass
class BalanceAtomic(Balance, Generic[T]):
    asset: T
    amount: AmountReadable
    amount_atomic: AmountAtomic
    decimals: int

    @staticmethod
    def empty(asset: T, decimals: int) -> "BalanceAtomic[T]":
        return BalanceAtomic(
            asset=asset,
            amount=Decimal(0),
            amount_atomic=0,
            decimals=decimals,
        )

    def serialize(self):
        """Serialize a balance to JSON."""
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        """Convert the Balance to a dictionary."""
        return {
            "asset": self.asset.to_dict(),
            "amount": format(self.amount, "f"),
            "amount_atomic": self.amount_atomic,
            "decimals": self.decimals,
        }

    @staticmethod
    def deserialize(balance_as_str: str):
        """Deserialize a balance from JSON as string."""
        balance_as_json = json.loads(balance_as_str)

        def deserialize_asset(asset: dict[str, Any]) -> Asset:
            ChildAsset = Token if asset["type"] == "TOKEN" else Basket

            return ChildAsset(
                id=asset["id"],
                name=asset["name"],
                display_name=asset["display_name"],
                ticker=asset["ticker"],
                address=asset["address"],
                decimals=asset["decimals"],
                categories=asset["categories"],
                description=asset["description"],
            )

        asset = deserialize_asset(balance_as_json["asset"])

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

        def deserialize_asset(token: dict[str, Any]) -> Asset:
            ChildAsset = Token if token["type"] == "TOKEN" else Basket

            return ChildAsset(
                id=token["id"],
                name=token["name"],
                display_name=token["display_name"],
                ticker=token["ticker"],
                address=token["address"],
                decimals=token["decimals"],
                categories=token["categories"],
                description=token["description"],
            )

        return deserialize_asset(asset_as_json)

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
