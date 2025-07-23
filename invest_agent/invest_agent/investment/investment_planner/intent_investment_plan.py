from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from protocol.asset import Asset
from pydantic import BaseModel, model_validator


@dataclass
class AssetBalance(BaseModel):
    asset: Asset
    amount: Decimal | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the AssetBalance to a dictionary."""
        return {
            "asset": self.asset.to_dict(),
            "amount": str(self.amount) if self.amount is not None else None,
        }


@dataclass
class IntentInvestmentPlanStep(BaseModel):
    buy_asset_with_amount: AssetBalance | None = None
    sell_asset_with_amount: AssetBalance | None = None

    @model_validator(mode="before")
    @classmethod
    def at_least_one_asset(cls, values: dict[str, Any]):
        """Ensure at least one of buy_asset_with_amount or sell_asset_with_amount is provided."""
        if not (
            values.get("buy_asset_with_amount") or values.get("sell_asset_with_amount")
        ):
            raise ValueError(
                "At least one of buy_asset_with_amount or sell_asset_with_amount must be provided."
            )

        return values

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
class IntentInvestmentPlan(BaseModel):
    steps: list[IntentInvestmentPlanStep]

    def to_dict(self) -> dict[str, Any]:
        """Convert the IntentInvestmentPlan to a dictionary."""
        return {"steps": [step.to_dict() for step in self.steps]}
