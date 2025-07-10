from decimal import Decimal
from protocol.asset import Asset
from invest_agent.chain.balance import Balance
from invest_agent.investment.investment_planner.investment_plan import (
    InvestmentPlan,
    InvestmentPlanStep,
)
from invest_agent.investment.investment_planner.investment_planner import (
    InvestmentPlanner,
)
from protocol.token import Token

from itertools import chain


# TODO: This code currently only handles BUY operations. Handle SELL operations as well.


class EqualInvestmentPlanner(InvestmentPlanner):
    def make_investment_plan(
        self, assets: list[Asset], investment_balance: Balance
    ) -> InvestmentPlan:
        """
        Create an investment plan from a list of assets and an investment balance.
        """
        step_amount = self.__round(investment_balance.amount / len(assets))

        steps = list(
            chain.from_iterable(
                [
                    self.__make_steps(asset, step_amount, investment_balance.token)
                    for asset in assets
                ]
            )
        )

        investment_plan = InvestmentPlan(steps=steps)

        print(f"Investment plan: {investment_plan}")
        return investment_plan

    def __make_steps(
        self, asset: Asset, step_amount: Decimal, investment_token: Token
    ) -> list[InvestmentPlanStep]:
        if isinstance(asset, Token):
            return [
                InvestmentPlanStep(
                    buy_token=asset,
                    sell_balance=Balance(token=investment_token, amount=step_amount),
                    basket=None,
                )
            ]

        step_amount_per_basket_token = self.__round(step_amount / len(asset.tokens))
        return [
            InvestmentPlanStep(
                buy_token=token,
                sell_balance=Balance(
                    token=investment_token, amount=step_amount_per_basket_token
                ),
                basket=asset,
            )
            for token in asset.tokens
        ]

    def __round(self, value: Decimal) -> Decimal:
        """
        Round a value to a given precision.
        """
        return value.quantize(Decimal("0.01"), rounding="ROUND_DOWN")
