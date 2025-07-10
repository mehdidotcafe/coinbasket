from dataclasses import dataclass
from decimal import Decimal

from protocol.asset import Asset


@dataclass
class AssetBalance:
    asset: Asset
    amount: Decimal = Decimal(1)


@dataclass
class IntentInvestmentPlanStep:
    buy_asset: Asset | None = None
    sell_balance: AssetBalance | None = None


@dataclass
class IntentInvestmentPlan:
    steps: list[IntentInvestmentPlanStep]
