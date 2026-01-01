from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from api.protocol.asset import Asset


@dataclass
class IntendedOrderBalance:
    asset: Asset
    amount: Decimal | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the IntendedOrderBalance to a dictionary."""
        return {
            "asset": self.asset.to_dict(),
            "amount": format(self.amount, "f") if self.amount is not None else None,
        }


@dataclass
class IntendedOrder:
    buy_asset_with_amount: IntendedOrderBalance | None = None
    sell_asset_with_amount: IntendedOrderBalance | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the IntentOrder to a dictionary."""
        return {
            "buy_asset_with_amount": self.buy_asset_with_amount.to_dict()
            if self.buy_asset_with_amount
            else None,
            "sell_asset_with_amount": self.sell_asset_with_amount.to_dict()
            if self.sell_asset_with_amount
            else None,
        }
