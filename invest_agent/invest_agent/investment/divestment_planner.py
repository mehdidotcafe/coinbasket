from abc import ABC, abstractmethod

from invest_agent.investment.basket_investment import BasketInvestment
from invest_agent.investment.investment_plan import InvestmentPlan


class DivestmentPlanner(ABC):
    @abstractmethod
    def make_divestment_plan(
        self, basket_investment: BasketInvestment
    ) -> InvestmentPlan:
        pass
