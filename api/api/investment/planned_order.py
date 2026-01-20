from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from api.address.address import Address
from api.investment.fees import Fees
from api.protocol.asset import Asset

PlannedOrderId = str


@dataclass
class PlannedOrderBalance:
    asset: Asset
    available_amount: Decimal
    amount: Decimal | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the PlannedOrderBalance to a dictionary."""
        return {
            "asset": self.asset.to_dict(),
            "amount": format(self.amount, "f") if self.amount is not None else None,
            "available_amount": format(self.available_amount, "f"),
        }


@dataclass
class PlannedOrder:
    id: PlannedOrderId
    address: Address
    sell_asset_with_amount: PlannedOrderBalance
    buy_asset_with_amount: PlannedOrderBalance
    fees: Fees

    def to_dict(self) -> dict[str, Any]:
        """Convert the PlannedOrder to a dictionary."""
        return {
            "id": self.id,
            "address": str(self.address),
            "buy_asset_with_amount": self.buy_asset_with_amount.to_dict(),
            "sell_asset_with_amount": self.sell_asset_with_amount.to_dict(),
            "fees": self.fees.to_dict(),
        }
