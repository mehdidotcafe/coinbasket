from abc import ABC, abstractmethod

from invest_agent.chain.balance import Balance
from protocol.asset import Asset
from invest_agent.investment.investment_planner.investment_plan import InvestmentPlan


class InvestmentPlanner(ABC):
    @abstractmethod
    def make_investment_plan(
        self, assets: list[Asset], investment_balance: Balance
    ) -> InvestmentPlan:
        pass
