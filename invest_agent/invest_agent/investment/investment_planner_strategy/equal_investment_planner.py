from protocol.basket import Basket
from invest_agent.chain.balance import Balance
from invest_agent.chain.chain import Chain
from invest_agent.investment.investment_plan import (
    InvestmentPlan,
    InvestmentPlanStep,
)
from invest_agent.investment.investment_planner import InvestmentPlanner
from invest_agent.investment.exception.insufficient_balance import (
    InsufficientBalance,
)


class EqualInvestmentPlanner(InvestmentPlanner):
    def __init__(self, chain: Chain):
        self.chain = chain

    async def make_investment_plan(self, basket: Basket) -> InvestmentPlan:
        """
        Create an investment plan from a basket.
        Throws an InsufficientBalanceException if the total balance is less than the minimum balance.
        """
        total_balance = await self.chain.get_balance()
        min_balance = await self.chain.get_min_balance()

        investment_balance = Balance(
            amount=total_balance.amount - min_balance.amount,
            token=total_balance.token,
        )

        if investment_balance.amount <= 0:
            raise InsufficientBalance(min_balance)

        step_amount = investment_balance.amount / len(basket.tokens)

        steps = [
            InvestmentPlanStep(
                token=coin,
                sell_balance=Balance(
                    token=investment_balance.token, amount=step_amount
                ),
            )
            for coin in basket.tokens
        ]

        investment_plan = InvestmentPlan(
            steps=steps, sell_total_balance=investment_balance
        )

        print(f"Investment plan: {investment_plan}")
        return investment_plan
