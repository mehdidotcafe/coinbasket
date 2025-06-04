from decimal import Decimal
from typing import Optional, TypedDict
from invest_agent.investment.basket_investment import BasketInvestment, Bid
from invest_agent.investment.exchange.exchange import Exchange
from invest_agent.investment.investment_parameters import (
    IntegratorFee,
    InvestmentParameters,
)
from invest_agent.storage.storage import Storage
from protocol.token import Token
from invest_agent.chain.chain import Chain


class Configuration(TypedDict):
    fee_integrator_address: Optional[str]
    fee_value_in_percentage: Optional[Decimal]


class GetWalletInTokenUseCase:
    def __init__(
        self,
        storage: Storage[BasketInvestment],
        exchange: Exchange,
        chain: Chain,
        configuration: Configuration,
    ):
        self.storage = storage
        self.exchange = exchange
        self.chain = chain
        self.configuration = configuration

    def execute(self, token: Token):
        basket_investment = self.storage.get("basket_investment")

        investment_parameters = InvestmentParameters(
            slippage_tolerance_in_percentage=Decimal("1"),
            integrator_fee=self.__make_integrator_fee(token),
        )

        return self.exchange.get_wallet_in_token(
            tokens_balance=[self.chain.get_balance()]
            + self.__map_basket_investment_bids_to_balances(
                basket_investment[0].bids if basket_investment else []
            ),
            token=token,
            investment_parameters=investment_parameters,
        )

    def __map_basket_investment_bids_to_balances(self, bids: list[Bid]):
        return [bid.buy_balance for bid in bids]

    def __make_integrator_fee(self, token: Token) -> IntegratorFee | None:
        return (
            None
            if self.configuration["fee_integrator_address"] is None
            or self.configuration["fee_value_in_percentage"] is None
            else IntegratorFee(
                recipient=self.configuration["fee_integrator_address"],
                value_in_percentage=self.configuration["fee_value_in_percentage"],
                token=token,
            )
        )
