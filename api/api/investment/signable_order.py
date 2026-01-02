from dataclasses import dataclass
from typing import Any

from api.address.address import Address
from api.chain.balance import BalanceAtomic
from api.investment.confirmed_order import ConfirmedOrderId
from api.investment.exchange.exchange import SignableTransaction

SignableOrderId = str


@dataclass
class SignableOrder:
    id: SignableOrderId
    confirmed_order_id: ConfirmedOrderId
    address: Address
    buy_balance: BalanceAtomic
    sell_balance: BalanceAtomic
    signature_payload: dict[str, Any] | None
    transaction: SignableTransaction

    def to_dict(self) -> dict[str, Any]:
        """Convert the SignableOrder to a dictionary."""
        return {
            "id": self.id,
            "confirmed_order_id": self.confirmed_order_id,
            "address": str(self.address),
            "buy_balance": self.buy_balance.to_dict(),
            "sell_balance": self.sell_balance.to_dict(),
            "signature_payload": self.signature_payload,
            "transaction": self.transaction.to_dict(),
        }
