from dataclasses import dataclass

from protocol.basket import Basket
from protocol.token import Token
from invest_agent.chain.balance import Balance


@dataclass
class InvestmentPlanStep:
    buy_token: Token
    sell_balance: Balance
    basket: Basket | None = None


@dataclass
class InvestmentPlan:
    steps: list[InvestmentPlanStep]
