from dataclasses import dataclass
from typing import Any

from api.chain.balance import BalanceAtomic
from api.investment.exchange.exchange import SignableTransaction


@dataclass
class SignableOrder:
    buy_balance: BalanceAtomic
    sell_balance: BalanceAtomic
    signature_payload: dict[str, Any] | None
    transaction: SignableTransaction

    def to_dict(self) -> dict[str, Any]:
        """Convert the SignableOrder to a dictionary."""
        return {
            "buy_balance": self.buy_balance.to_dict(),
            "sell_balance": self.sell_balance.to_dict(),
            "signature_payload": self.signature_payload,
            "transaction": self.transaction.to_dict(),
        }
