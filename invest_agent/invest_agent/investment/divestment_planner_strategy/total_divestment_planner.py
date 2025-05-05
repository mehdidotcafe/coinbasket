from decimal import Decimal
from invest_agent.chain.balance import Balance
from invest_agent.chain.chain import Chain
from invest_agent.investment.divestment_planner import DivestmentPlanner
from invest_agent.investment.investment_plan import InvestmentPlan, InvestmentPlanStep
from invest_agent.investment.investment_result import (
    InvestmentResult,
    InvestmentResultBid,
)


class TotalDivestmentPlanner(DivestmentPlanner):
    def __init__(self, chain: Chain):
        self.chain = chain

    def make_divestment_plan(
        self, investment_result: InvestmentResult
    ) -> InvestmentPlan:
        """Create a divestment plan for the total divestment of the basket."""
        token = self.chain.get_base_token()
        divestment_plan = InvestmentPlan(
            steps=[self.__map_bid_to_step(bid) for bid in investment_result.bids],
            balance=Balance(amount=Decimal(0), token=token),
        )

        print(f"Divestment plan: {divestment_plan}")
        return divestment_plan

    def __map_bid_to_step(
        self, investment_result_bid: InvestmentResultBid
    ) -> InvestmentPlanStep:
        """Map a bid to a divestment step."""
        return InvestmentPlanStep(
            token=investment_result_bid.balance_out.token,
            amount=investment_result_bid.balance_out.amount,
        )
