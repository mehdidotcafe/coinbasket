from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Literal

from api.address.address import Address
from api.protocol.asset import Asset

IntendedOrderId = str

IntendedOrderType = Literal["SELL", "BUY"]


@dataclass
class IntendedOrder:
    id: IntendedOrderId
    address: Address
    type: IntendedOrderType
    sell_asset: Asset | None = None
    buy_asset: Asset | None = None
    amount: Decimal | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the IntentOrder to a dictionary."""
        return {
            "id": self.id,
            "address": str(self.address),
            "sell_asset": self.sell_asset.to_dict() if self.sell_asset else None,
            "buy_asset": self.buy_asset.to_dict() if self.buy_asset else None,
            "type": self.type,
            "amount": format(self.amount, "f") if self.amount is not None else None,
        }
