from protocol.basket import Basket
from invest_agent.investment.exchange.exchange import Exchange
from invest_agent.investment.investment_planner_strategy.insufficient_balance_exception import (
    InsufficientBalanceException,
)
from invest_agent.investment.investment_planner import InvestmentPlanner
from invest_agent.investment.investment_result import InvestmentResult
from invest_agent.storage.storage import Storage


class BasketInvestUseCase:
    def __init__(
        self,
        investment_planner: InvestmentPlanner,
        exchange: Exchange,
        storage: Storage[InvestmentResult],
    ):
        self.investment_planner = investment_planner
        self.exchange = exchange
        self.storage = storage

    def execute(self, basket: Basket):
        try:
            investment_result = self.exchange.execute_investment_plan(
                self.investment_planner.make_investment_plan(basket)
            )

            self.storage.set("investment_result", investment_result, 1)

            return "Investment success.", investment_result
        except InsufficientBalanceException as e:
            return e.message, None
        except Exception as e:
            return str(e), None
