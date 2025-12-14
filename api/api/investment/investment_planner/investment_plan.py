from dataclasses import dataclass

from api.chain.balance import Balance


@dataclass
class InvestmentPlanStep:
    buy_balance: Balance
    sell_balance: Balance


@dataclass
class InvestmentPlan:
    steps: list[InvestmentPlanStep]
