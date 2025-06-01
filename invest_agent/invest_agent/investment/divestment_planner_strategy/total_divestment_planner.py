from decimal import Decimal
from invest_agent.chain.balance import Balance
from invest_agent.chain.chain import Chain
from invest_agent.investment.basket_investment import BasketInvestment, Bid
from invest_agent.investment.divestment_planner import DivestmentPlanner
from invest_agent.investment.investment_plan import InvestmentPlan, InvestmentPlanStep


class TotalDivestmentPlanner(DivestmentPlanner):
    def __init__(self, chain: Chain):
        self.chain = chain

    def make_divestment_plan(
        self, basket_investment: BasketInvestment
    ) -> InvestmentPlan:
        """Create a divestment plan for the total divestment of the basket."""
        token = self.chain.get_base_token()
        divestment_plan = InvestmentPlan(
            steps=[self.__map_bid_to_step(bid) for bid in basket_investment.bids],
            balance=Balance(amount=Decimal(0), token=token),
        )

        print(f"Divestment plan: {divestment_plan}")
        return divestment_plan

    def __map_bid_to_step(self, basket_investment_bid: Bid) -> InvestmentPlanStep:
        """Map a bid to a divestment step."""
        return InvestmentPlanStep(
            token=basket_investment_bid.buy_balance.token,
            amount=basket_investment_bid.buy_balance.amount,
        )
