from coinbasket.investment.divestment_planner import DivestmentPlanner
from coinbasket.investment.exchange.exchange import Exchange
from coinbasket.investment.investment_result import InvestmentResult
from coinbasket.storage.storage import Storage


class BasketDivestUseCase:
    """Divest / sell the basket create by the user."""

    def __init__(
        self,
        divestment_planner: DivestmentPlanner,
        exchange: Exchange,
        storage: Storage[InvestmentResult],
    ):
        self.divestment_planner = divestment_planner
        self.exchange = exchange
        self.storage = storage

    def execute(self):
        """Execute the divestment of the basket."""
        investment_result = self.storage.get("investment_result")

        if investment_result is None:
            return "Divestment error: No investment basket found.", None

        # TODO: Check balance

        try:
            divestment_result = self.exchange.execute_divestment_plan(
                self.divestment_planner.make_divestment_plan(investment_result[0])
            )

            self.storage.remove("investment_result")
        except Exception as e:
            return f"Divestment error: {str(e)}", None

        return "Divestment success.", divestment_result
