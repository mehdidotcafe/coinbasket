from dataclasses import dataclass
from typing_extensions import List

from protocol.token import Token
from invest_agent.chain.balance import Balance


@dataclass
class InvestmentPlanStep:
    token: Token
    sell_balance: Balance


@dataclass
class InvestmentPlan:
    steps: List[InvestmentPlanStep]
    sell_total_balance: Balance
