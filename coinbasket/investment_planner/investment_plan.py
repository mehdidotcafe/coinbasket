from dataclasses import dataclass
from typing_extensions import List

from coinbasket.basket import Token


@dataclass
class InvestmentPlanStep:
    token: Token
    amount: float


@dataclass
class InvestmentPlan:
    steps: List[InvestmentPlanStep]
    total_amount: float
