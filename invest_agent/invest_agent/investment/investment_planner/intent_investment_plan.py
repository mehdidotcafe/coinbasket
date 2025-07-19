from dataclasses import dataclass
from decimal import Decimal

from protocol.asset import Asset


@dataclass
class AssetBalance:
    asset: Asset
    amount: Decimal | None = None


@dataclass
class BuyIntentInvestmentPlanStep:
    buy_token_or_basket: Asset
    buy_token_or_basket_quantity: Decimal | None = None


@dataclass
class BuyIntentInvestmentPlan:
    steps: list[BuyIntentInvestmentPlanStep]


@dataclass
class IntentInvestmentPlanStep:
    buy_balance: AssetBalance | None = None
    sell_balance: AssetBalance | None = None


@dataclass
class IntentInvestmentPlan:
    steps: list[IntentInvestmentPlanStep]
