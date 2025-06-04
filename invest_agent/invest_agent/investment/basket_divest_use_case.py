from decimal import Decimal
from typing import Optional, TypedDict
from invest_agent.chain.chain import Chain
from invest_agent.datetime.date_time import DateTime
from invest_agent.investment.basket_investment import BasketInvestment, Bid
from invest_agent.investment.divestment_planner import DivestmentPlanner
from invest_agent.investment.exception.no_basket_investment import NoBasketInvestment
from invest_agent.investment.exchange.exchange import Exchange
from invest_agent.investment.investment_parameters import (
    IntegratorFee,
    InvestmentParameters,
)
from invest_agent.storage.storage import Storage


class Configuration(TypedDict):
    fee_integrator_address: Optional[str]
    fee_value_in_percentage: Optional[Decimal]


class BasketDivestUseCase:
    """Divest / sell the basket create by the user."""

    def __init__(
        self,
        divestment_planner: DivestmentPlanner,
        exchange: Exchange,
        storage: Storage[BasketInvestment],
        date_time: DateTime,
        chain: Chain,
        configuration: Configuration,
    ):
        self.divestment_planner = divestment_planner
        self.exchange = exchange
        self.storage = storage
        self.date_time = date_time
        self.chain = chain
        self.configuration = configuration

    def execute(self):
        """Execute the divestment of the basket."""
        basket_investment = self.storage.get("basket_investment")

        if basket_investment is None:
            raise NoBasketInvestment()

        # TODO: Check balance

        investment_parameters = InvestmentParameters(
            slippage_tolerance_in_percentage=Decimal("1"),
            integrator_fee=self.__make_integrator_fee(),
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

    def __make_integrator_fee(self) -> IntegratorFee | None:
        return (
            None
            if self.configuration["fee_integrator_address"] is None
            or self.configuration["fee_value_in_percentage"] is None
            else IntegratorFee(
                recipient=self.configuration["fee_integrator_address"],
                value_in_percentage=self.configuration["fee_value_in_percentage"],
                token=self.chain.get_base_token(),
            )
        )
