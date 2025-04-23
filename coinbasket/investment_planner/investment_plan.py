from dataclasses import dataclass
from typing_extensions import List

from coinbasket.basket import Coin


@dataclass
class InvestmentPlanStep:
    coin: Coin
    amount: float


@dataclass
class InvestmentPlan:
    steps: List[InvestmentPlanStep]
    total_amount: float
