from abc import ABC, abstractmethod

from invest_agent.investment.investment_plan import InvestmentPlan
from invest_agent.investment.investment_result import InvestmentResult


class DivestmentPlanner(ABC):
    @abstractmethod
    def make_divestment_plan(
        self, investment_result: InvestmentResult
    ) -> InvestmentPlan:
        pass
