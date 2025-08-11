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
                "amount": str(self.amount),
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

    def serialize(self):
        """Serialize a balance to JSON."""
        return json.dumps(
            {
                "asset": self.asset.to_dict(),
                "amount": str(self.amount),
                "amount_atomic": self.amount_atomic,
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
        )
