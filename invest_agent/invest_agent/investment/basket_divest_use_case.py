from decimal import Decimal
from invest_agent.datetime.date_time import DateTime
from invest_agent.investment.basket_investment import BasketInvestment, Bid
from invest_agent.investment.divestment_planner import DivestmentPlanner
from invest_agent.investment.exception.no_basket_investment import NoBasketInvestment
from invest_agent.investment.exchange.exchange import Exchange
from invest_agent.investment.investment_parameters import InvestmentParameters
from invest_agent.storage.storage import Storage


class BasketDivestUseCase:
    """Divest / sell the basket create by the user."""

    def __init__(
        self,
        divestment_planner: DivestmentPlanner,
        exchange: Exchange,
        storage: Storage[BasketInvestment],
        date_time: DateTime,
    ):
        self.divestment_planner = divestment_planner
        self.exchange = exchange
        self.storage = storage
        self.date_time = date_time

    def execute(self):
        """Execute the divestment of the basket."""
        basket_investment = self.storage.get("basket_investment")

        if basket_investment is None:
            raise NoBasketInvestment()

        # TODO: Check balance

        investment_parameters = InvestmentParameters(
            slippage_tolerance_in_percentage=Decimal("1"),
        )

        try:
            bids = self.exchange.execute_divestment_plan(
                self.divestment_planner.make_divestment_plan(basket_investment[0]),
                investment_parameters,
            )

            basket_divestment = self.__map_bids_and_basket_to_basket_investment(
                bids, basket_investment[0]
            )

            self.storage.remove("basket_investment")
        except Exception as e:
            return f"Divestment error: {str(e)}", None

        return "Divestment success.", basket_divestment

    def __map_bids_and_basket_to_basket_investment(
        self, bids: list[Bid], basket: BasketInvestment
    ) -> BasketInvestment:
        return BasketInvestment(
            name=basket.name,
            description=basket.description,
            type="basket divestment",
            invested_at=self.date_time.now_str(),
            bids=bids,
            status="invested",
        )
