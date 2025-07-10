from decimal import Decimal
from invest_agent.chain.chain import Chain
from invest_agent.investment.exchange.exchange import Exchange
from invest_agent.investment.investment_parameters import InvestmentParameters
from invest_agent.investment.investment_planner.investment_planner import (
    InvestmentPlanner,
)
from protocol.asset import Asset


class BuyOrSellAssetsUseCase:
    """Use case for buying or selling assets in the agent's wallet."""

    def __init__(
        self, chain: Chain, exchange: Exchange, investment_planner: InvestmentPlanner
    ):
        self.chain = chain
        self.exchange = exchange
        self.investment_planner = investment_planner

    async def execute(self, assets: list[Asset]):
        """Buy or sell assets in the agent's wallet.

        Args:
            assets: The assets to buy or sell. It can be a basket or a token.
        """
        balance = await self.chain.get_available_balance()

        investment_plan = self.investment_planner.make_investment_plan(
            assets=assets, investment_balance=balance
        )

        return await self.exchange.execute_investment_plan(
            investment_plan=investment_plan,
            investment_parameters=InvestmentParameters(
                slippage_tolerance_in_percentage=Decimal("1"),
            ),
        )
