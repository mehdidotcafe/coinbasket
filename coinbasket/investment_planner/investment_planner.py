from abc import ABC, abstractmethod

from coinbasket.basket import Basket
from coinbasket.investment_planner.investment_plan import InvestmentPlan


class InvestmentPlanner(ABC):
    @abstractmethod
    def make_investment_plan(self, basket: Basket) -> InvestmentPlan:
        pass
