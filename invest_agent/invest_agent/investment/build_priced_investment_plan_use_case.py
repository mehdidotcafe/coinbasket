from decimal import Decimal
from typing import cast
from invest_agent.chain.balance import BalanceAtomic
from invest_agent.chain.chain import Chain
from invest_agent.investment.calculator.asset_balance_converter import (
    AssetBalanceConverter,
)
from invest_agent.investment.exchange.exchange import Exchange
from invest_agent.investment.investment_parameters import InvestmentParameters
from invest_agent.investment.investment_planner.intent_investment_plan import (
    IntentInvestmentPlan,
)
from invest_agent.investment.investment_planner.priced_investment_plan import (
    PricedInvestmentPlan,
    PricedInvestmentPlanBalance,
    PricedInvestmentPlanStep,
)
from invest_agent.portfolio.holding.holding import Holding
from invest_agent.portfolio.posting.posting_repository import PostingRepository
from protocol.asset import Asset
from protocol.token import Token


class BuildPricedInvestmentPlanUseCase:
    def __init__(
        self,
        exchange: Exchange,
        chain: Chain,
        posting_repository: PostingRepository,
        asset_balance_converter: AssetBalanceConverter,
    ):
        self.exchange = exchange
        self.chain = chain
        self.posting_repository = posting_repository
        self.asset_balance_converter = asset_balance_converter

    async def execute(
        self, intent_investment_plan: IntentInvestmentPlan
    ) -> PricedInvestmentPlan:
        steps: list[PricedInvestmentPlanStep] = []

        holdings = await self.posting_repository.get_holding_balances()
        holding_balances = await self._get_all_holding_balances(holdings)

        for step in intent_investment_plan.steps:
            sell_asset = (
                step.sell_asset_with_amount.asset
                if step.sell_asset_with_amount
                else self.chain.get_base_token()
            )
            sell_token = sell_asset.get_pricing_token()

            sell_asset_available_amount = self._get_available_amount(
                holding_balances, sell_asset
            )

            buy_asset = (
                step.buy_asset_with_amount.asset
                if step.buy_asset_with_amount
                else self.chain.get_base_token()
            )
            buy_token = buy_asset.get_pricing_token()

            buy_asset_available_amount = self._get_available_amount(
                holding_balances, buy_asset
            )

            if (
                isinstance(sell_asset, Token)
                and sell_asset.address == buy_token.address
            ):
                continue

            if step.sell_asset_with_amount and step.sell_asset_with_amount.amount:
                (
                    sell_balance_amount_atomic,
                    sell_balance_decimals,
                ) = await self.chain.convert_amount_to_amount_atomic(
                    token=sell_token,
                    amount_readable=step.sell_asset_with_amount.amount,
                )

                converted_asset_balance = await self.asset_balance_converter.convert(
                    sell_balance=BalanceAtomic[Asset](
                        asset=sell_asset,
                        amount=step.sell_asset_with_amount.amount,
                        amount_atomic=sell_balance_amount_atomic,
                        decimals=sell_balance_decimals,
                    ),
                    buy_asset=buy_asset,
                    holdings=holdings,
                )

                steps.append(
                    PricedInvestmentPlanStep(
                        sell_asset_with_amount=PricedInvestmentPlanBalance(
                            asset=sell_asset,
                            amount=converted_asset_balance.total_balance.sell_balance.amount,
                            available_amount=sell_asset_available_amount,
                        ),
                        buy_asset_with_amount=PricedInvestmentPlanBalance(
                            asset=buy_asset,
                            amount=converted_asset_balance.total_balance.buy_balance.amount,
                            available_amount=buy_asset_available_amount,
                        ),
                    )
                )
                continue

            if step.buy_asset_with_amount and step.buy_asset_with_amount.amount:
                buy_token_amount = (
                    step.buy_asset_with_amount.amount * buy_asset.get_denomination()
                )
                (
                    buy_balance_amount_atomic,
                    buy_balance_decimals,
                ) = await self.chain.convert_amount_to_amount_atomic(
                    token=buy_token,
                    amount_readable=buy_token_amount,
                )
                buy_balance = BalanceAtomic[Token](
                    asset=buy_token,
                    amount=buy_token_amount,
                    amount_atomic=buy_balance_amount_atomic,
                    decimals=buy_balance_decimals,
                )

                # TODO: Flipping sell and buy token is inaccurate
                converted_balance = await self.exchange.convert_balance_to_token(
                    balance=buy_balance,
                    token=sell_token,
                    investment_parameters=InvestmentParameters(
                        slippage_tolerance_in_percentage=Decimal(1)
                    ),
                )

                steps.append(
                    PricedInvestmentPlanStep(
                        sell_asset_with_amount=PricedInvestmentPlanBalance(
                            asset=sell_asset,
                            amount=converted_balance.buy_balance.amount
                            / sell_asset.get_denomination(),
                            available_amount=sell_asset_available_amount,
                        ),
                        buy_asset_with_amount=PricedInvestmentPlanBalance(
                            asset=buy_asset,
                            amount=converted_balance.sell_balance.amount
                            / buy_asset.get_denomination(),
                            available_amount=buy_asset_available_amount,
                        ),
                    )
                )
                continue

            if step.sell_asset_with_amount:
                steps.append(
                    PricedInvestmentPlanStep(
                        sell_asset_with_amount=PricedInvestmentPlanBalance(
                            asset=sell_asset,
                            amount=None,
                            available_amount=sell_asset_available_amount,
                        ),
                        buy_asset_with_amount=PricedInvestmentPlanBalance(
                            asset=buy_asset,
                            amount=step.buy_asset_with_amount.amount
                            if step.buy_asset_with_amount
                            else None,
                            available_amount=buy_asset_available_amount,
                        ),
                    )
                )
                continue

            if step.buy_asset_with_amount:
                steps.append(
                    PricedInvestmentPlanStep(
                        sell_asset_with_amount=PricedInvestmentPlanBalance(
                            asset=sell_asset,
                            amount=step.sell_asset_with_amount.amount
                            if step.sell_asset_with_amount
                            else None,
                            available_amount=sell_asset_available_amount,
                        ),
                        buy_asset_with_amount=PricedInvestmentPlanBalance(
                            asset=buy_asset,
                            amount=None,
                            available_amount=buy_asset_available_amount,
                        ),
                    )
                )
                continue

        return PricedInvestmentPlan(
            steps=steps,
        )

    def _get_available_amount(
        self, holding_balances_per_token: dict[str, BalanceAtomic], asset: Asset
    ) -> Decimal:
        holding_balance = holding_balances_per_token.get(asset.id)

        return holding_balance.amount if holding_balance else Decimal("0")

    async def _get_all_holding_balances(
        self, holdings: list[Holding]
    ) -> dict[str, BalanceAtomic]:
        available_balance = await self.chain.get_native_token_balance()

        holding_balances_per_token = {
            balance.asset.id: balance
            for balance in cast(
                list[BalanceAtomic],
                [*[holding.balance for holding in holdings], available_balance],
            )
        }

        return holding_balances_per_token
