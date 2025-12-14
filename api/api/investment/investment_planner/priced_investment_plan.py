from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from protocol.asset import Asset


@dataclass
class PricedInvestmentPlanBalance:
    asset: Asset
    available_amount: Decimal
    amount: Decimal | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the PricedInvestmentPlanBalance to a dictionary."""
        return {
            "asset": self.asset.to_dict(),
            "amount": format(self.amount, "f") if self.amount is not None else None,
            "available_amount": format(self.available_amount, "f"),
        }


@dataclass
class PricedInvestmentPlanStep:
    buy_asset_with_amount: PricedInvestmentPlanBalance | None = None
    sell_asset_with_amount: PricedInvestmentPlanBalance | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the PricedInvestmentPlanStep to a dictionary."""
        return {
            "buy_asset_with_amount": self.buy_asset_with_amount.to_dict()
            if self.buy_asset_with_amount
            else None,
            "sell_asset_with_amount": self.sell_asset_with_amount.to_dict()
            if self.sell_asset_with_amount
            else None,
        }


@dataclass
class PricedInvestmentPlan:
    steps: list[PricedInvestmentPlanStep]

    def to_dict(self) -> dict[str, Any]:
        """Convert the PricedInvestmentPlan to a dictionary."""
        return {"steps": [step.to_dict() for step in self.steps]}
