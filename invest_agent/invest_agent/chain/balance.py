from dataclasses import asdict, dataclass
from decimal import Decimal
import json

from protocol.token import Token


@dataclass
class Balance:
    token: Token
    amount: Decimal

    def serialize(self):
        """Serialize a balance to JSON."""
        return json.dumps(
            {
                "token": asdict(self.token),
                "amount": str(self.amount),
            }
        )

    @staticmethod
    def deserialize(balance_as_str: str):
        """Deserialize a balance from JSON as string."""
        balance_as_json = json.loads(balance_as_str)

        return Balance(
            token=Token(
                id=balance_as_json["token"]["id"],
                name=balance_as_json["token"]["name"],
                display_name=balance_as_json["token"]["display_name"],
                ticker=balance_as_json["token"]["ticker"],
                address=balance_as_json["token"]["address"],
            ),
            amount=Decimal(balance_as_json["amount"]),
        )
