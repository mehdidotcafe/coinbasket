from coinbasket.basket import Basket
from coinbasket.investment.exchange.exchange import Exchange
from coinbasket.investment.insufficient_balance_exception import (
    InsufficientBalanceException,
)
from coinbasket.investment.investment_planner import InvestmentPlanner
from coinbasket.storage.storage import Storage


class InvestUseCase:
    def __init__(
        self,
        investment_planner: InvestmentPlanner,
        exchange: Exchange,
        storage: Storage,
    ):
        self.investment_planner = investment_planner
        self.exchange = exchange
        self.storage = storage

    def execute(self, basket: Basket):
        try:
            investment_result = self.exchange.execute_investment_plan(
                self.investment_planner.make_investment_plan(basket)
            )

            self.storage.set("investment_result", investment_result)

            return "Investment success.", investment_result
        except InsufficientBalanceException as e:
            return e.message
