from abc import ABC, abstractmethod

from coinbasket.investment.investment_plan import InvestmentPlan
from coinbasket.investment.investment_result import InvestmentResult


class DivestmentPlanner(ABC):
    @abstractmethod
    def make_divestment_plan(
        self, investment_result: InvestmentResult
    ) -> InvestmentPlan:
        pass
