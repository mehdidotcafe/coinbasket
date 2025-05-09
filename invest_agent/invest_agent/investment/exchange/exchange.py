from abc import ABC, abstractmethod

from invest_agent.investment.basket_investment import Bid
from invest_agent.investment.investment_plan import InvestmentPlan


class Exchange(ABC):
    @abstractmethod
    def execute_investment_plan(self, investment_plan: InvestmentPlan) -> list[Bid]:  # noqa: F821
        pass

    @abstractmethod
    def execute_divestment_plan(self, divestment_plan: InvestmentPlan) -> list[Bid]:
        pass
