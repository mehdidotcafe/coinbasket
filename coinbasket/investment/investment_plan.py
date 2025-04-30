from dataclasses import dataclass
from typing_extensions import List

from coinbasket.basket import Token
from coinbasket.chain.balance import Balance


@dataclass
class InvestmentPlanStep:
    token: Token
    amount: float


@dataclass
class InvestmentPlan:
    steps: List[InvestmentPlanStep]
    balance: Balance
