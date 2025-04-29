from coinbasket.basket import Basket
from coinbasket.chain.chain import Chain
from coinbasket.investment_planner.investment_plan import (
    InvestmentPlan,
    InvestmentPlanStep,
)
from coinbasket.investment_planner.investment_planner import InvestmentPlanner
from .insufficient_balance_exception import (
    InsufficientBalanceException,
)


class EqualInvestmentPlanner(InvestmentPlanner):
    def __init__(self, chain: Chain):
        self.chain = chain

    def make_investment_plan(self, basket: Basket) -> InvestmentPlan:
        """
        Create an investment plan from a basket.
        Throws an InsufficientBalanceException if the total balance is less than the minimum balance.
        """
        total_balance = self.chain.get_balance()
        min_balance = self.chain.get_min_balance()

        if total_balance.amount <= min_balance.amount:
            raise InsufficientBalanceException(min_balance)

        step_amount = total_balance.amount / len(basket.tokens)

        steps = [
            InvestmentPlanStep(token=coin, amount=step_amount) for coin in basket.tokens
        ]

        return InvestmentPlan(steps=steps, balance=total_balance)
