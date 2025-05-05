from abc import ABC, abstractmethod

from invest_agent.investment.investment_plan import InvestmentPlan
from invest_agent.investment.investment_result import InvestmentResult


class Exchange(ABC):
    @abstractmethod
    def execute_investment_plan(
        self, investment_plan: InvestmentPlan
    ) -> InvestmentResult:
        pass

    @abstractmethod
    def execute_divestment_plan(
        self, divestment_plan: InvestmentPlan
    ) -> InvestmentResult:
        pass
