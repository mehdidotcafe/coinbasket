from abc import ABC, abstractmethod

from coinbasket.investment.investment_plan import InvestmentPlan
from coinbasket.investment.investment_result import InvestmentResult


class Exchange(ABC):
    @abstractmethod
    def execute_investment_plan(
        self, investment_plan: InvestmentPlan
    ) -> InvestmentResult:
        pass
