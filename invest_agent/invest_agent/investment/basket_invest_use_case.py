from decimal import Decimal
from invest_agent.datetime.date_time import DateTime
from invest_agent.investment.basket_investment import BasketInvestment, Bid
from invest_agent.investment.exception.basked_already_invested import (
    BasketAlreadyInvested,
)
from invest_agent.investment.investment_parameters import InvestmentParameters
from protocol.basket import Basket
from invest_agent.investment.exchange.exchange import Exchange
from invest_agent.investment.investment_planner import InvestmentPlanner
from invest_agent.storage.storage import Storage


class BasketInvestUseCase:
    def __init__(
        self,
        investment_planner: InvestmentPlanner,
        exchange: Exchange,
        storage: Storage[BasketInvestment],
        date_time: DateTime,
    ):
        self.investment_planner = investment_planner
        self.exchange = exchange
        self.storage = storage
        self.date_time = date_time

    async def execute(self, basket: Basket):
        if self.storage.has("basket_investment"):
            raise BasketAlreadyInvested()

        investment_parameters = InvestmentParameters(
            slippage_tolerance_in_percentage=Decimal("1"),
        )

        try:
            bids = await self.exchange.execute_investment_plan(
                await self.investment_planner.make_investment_plan(basket),
                investment_parameters,
            )
            basket_investment = self.__map_bids_and_basket_to_basket_investment(
                bids, basket
            )

            self.storage.set("basket_investment", basket_investment, 1)

            return "Investment success.", basket_investment
        except Exception as e:
            return str(e), None

    def __map_bids_and_basket_to_basket_investment(
        self, bids: list[Bid], basket: Basket
    ) -> BasketInvestment:
        return BasketInvestment(
            name=basket.name,
            description=basket.description,
            type="basket investment",
            invested_at=self.date_time.now_str(),
            bids=bids,
            status="invested",
        )
