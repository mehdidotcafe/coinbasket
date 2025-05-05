from abc import ABC, abstractmethod

from invest_agent.basket import Basket
from invest_agent.investment.investment_plan import InvestmentPlan


class InvestmentPlanner(ABC):
    @abstractmethod
    def make_investment_plan(self, basket: Basket) -> InvestmentPlan:
        pass
