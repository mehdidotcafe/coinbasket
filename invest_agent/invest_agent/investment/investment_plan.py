from dataclasses import dataclass
from decimal import Decimal
from typing_extensions import List

from protocol.token import Token
from invest_agent.chain.balance import Balance


@dataclass
class InvestmentPlanStep:
    token: Token
    amount: Decimal


@dataclass
class InvestmentPlan:
    steps: List[InvestmentPlanStep]
    balance: Balance
