from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from protocol.asset import Asset


@dataclass
class IntentInvestmentPlanBalance:
    asset: Asset
    amount: Decimal | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the IntentInvestmentPlanBalance to a dictionary."""
        return {
            "asset": self.asset.to_dict(),
            "amount": format(self.amount, "f") if self.amount is not None else None,
        }


@dataclass
class IntentInvestmentPlanStep:
    buy_asset_with_amount: IntentInvestmentPlanBalance | None = None
    sell_asset_with_amount: IntentInvestmentPlanBalance | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the IntentInvestmentPlanStep to a dictionary."""
        return {
            "buy_asset_with_amount": self.buy_asset_with_amount.to_dict()
            if self.buy_asset_with_amount
            else None,
            "sell_asset_with_amount": self.sell_asset_with_amount.to_dict()
            if self.sell_asset_with_amount
            else None,
        }


@dataclass
class IntentInvestmentPlan:
    steps: list[IntentInvestmentPlanStep]

    def to_dict(self) -> dict[str, Any]:
        """Convert the IntentInvestmentPlan to a dictionary."""
        return {"steps": [step.to_dict() for step in self.steps]}
