from decimal import Decimal
from api.investment.exchange.exchange import Exchange
from api.investment.investment_planner.investment_plan import (
    InvestmentPlanStep,
)
from api.investment.investment_parameters import InvestmentParameters
from api.investment.investment_planner.quoted_investment_plan_step import (
    QuotedInvestmentPlanStep,
)


investment_parameters = InvestmentParameters(
    slippage_tolerance_in_percentage=Decimal("1"),
)


class BuildQuotedInvestmentPlanStepUseCase:
    def __init__(self, exchange: Exchange):
        self.exchange = exchange

    async def execute(self, step: InvestmentPlanStep):
        signed_swap = await self.exchange.get_signable_swap(
            sell_balance=step.sell_balance,
            buy_balance=step.buy_balance,
            investment_parameters=investment_parameters,
        )

        return QuotedInvestmentPlanStep(
            buy_balance=signed_swap.buy_balance,
            sell_balance=signed_swap.sell_balance,
            signature_payload=signed_swap.signature_payload,
            transaction=signed_swap.transaction,
        )
