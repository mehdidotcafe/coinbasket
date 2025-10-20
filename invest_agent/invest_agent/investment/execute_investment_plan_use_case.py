import asyncio
from dataclasses import dataclass
from decimal import ROUND_DOWN, Decimal
from typing import cast
from invest_agent.chain.balance import BalanceAtomic
from invest_agent.chain.chain import Chain
from invest_agent.datetime.date_time import DateTime
from invest_agent.investment.exception.cannot_swap_basket_for_another_exception import (
    CannotSwapBasketForAnotherException,
)
from invest_agent.investment.exception.insufficient_asset_balance import (
    InsufficientAssetBalance,
)
from invest_agent.investment.exchange.exchange import Exchange
from invest_agent.investment.investment_parameters import InvestmentParameters
from invest_agent.investment.investment_planner.investment_plan import (
    InvestmentPlan,
    InvestmentPlanStep,
)
from invest_agent.investment.order.order import Order, OrderAssetType
from invest_agent.investment.order.order_submitter import OrderSubmitter
from invest_agent.portfolio.posting.posting_repository import PostingRepository
from protocol.asset import Asset
from protocol.basket import Basket
from protocol.token import Token
from shared.id_generator.id_generator import IdGenerator


@dataclass
class PricedInvestmentStep:
    id: str
    sell_balance: BalanceAtomic
    buy_balance: BalanceAtomic
    asset_type: OrderAssetType
    basket_id: str | None = None
    parent_id: str | None = None


@dataclass
class PricedInvestmentPlan:
    steps: list[list[PricedInvestmentStep]]


investment_parameters = InvestmentParameters(
    slippage_tolerance_in_percentage=Decimal("1"),
)


class ExecuteInvestmentPlanUseCase:
    """Use case executing an investment plan."""

    def __init__(
        self,
        id_generator: IdGenerator,
        date_time: DateTime,
        chain: Chain,
        order_submitter: OrderSubmitter,
        exchange: Exchange,
        posting_repository: PostingRepository,
    ):
        self.id_generator = id_generator
        self.date_time = date_time
        self.chain = chain
        self.order_submitter = order_submitter
        self.exchange = exchange
        self.posting_repository = posting_repository

    async def execute(self, investment_plan: InvestmentPlan) -> list[list[Order]]:
        """Swap assets.

        Args:
            investment_plan: The investment plan to execute.
        Returns:
            A list of Orders created for the assets in the investment plan.
        """

        priced_investment_plan = await self.__price_investment_plan(investment_plan)

        await self._assert_has_sufficient_balances(priced_investment_plan)

        orders = [
            self.__map_priced_investment_plan_step_to_orders(step)
            for step in priced_investment_plan.steps
        ]

        if len(orders) == 0:
            return []
        return await self.order_submitter.submit_orders(orders)

    def __map_priced_investment_plan_step_to_orders(
        self, step_matrix: list[PricedInvestmentStep]
    ) -> list[Order]:
        return [
            Order(
                id=step.id,
                parent_order_id=step.parent_id,
                sell_balance=step.sell_balance,
                buy_balance=step.buy_balance,
                type=self.__get_order_type(
                    step.sell_balance.asset, step.buy_balance.asset
                ),
                tries=[],
                created_at=self.date_time.now(),
                status="PENDING",
                trigger="MANUAL",
                asset_type=step.asset_type,
                basket_id=step.basket_id,
            )
            for step in step_matrix
        ]

    def __get_order_type(self, sell_asset: Asset, buy_asset: Asset):
        native_token = self.chain.get_base_token()

        if sell_asset == native_token:
            return "BUY"
        if buy_asset == native_token:
            return "SELL"
        return "SWAP"

    async def __price_investment_plan(
        self, investment_plan: InvestmentPlan
    ) -> PricedInvestmentPlan:
        steps: list[list[PricedInvestmentStep]] = []

        # TODO: Make async
        for step in investment_plan.steps:
            if step.sell_balance.amount <= 0:
                continue
            priced_step = await self.__price_investment_plan_step(step)
            steps.append(priced_step)

        return PricedInvestmentPlan(steps)

    async def __price_investment_plan_step(
        self, step: InvestmentPlanStep
    ) -> list[PricedInvestmentStep]:
        buy_balance = step.buy_balance
        sell_balance = step.sell_balance

        if isinstance(buy_balance.asset, Basket) and isinstance(
            sell_balance.asset, Basket
        ):
            raise CannotSwapBasketForAnotherException()

        (
            sell_balance_amount_atomic,
            sell_balance_decimals,
        ) = await self.chain.convert_amount_to_amount_atomic(
            token=sell_balance.asset.get_pricing_token(),
            amount_readable=sell_balance.amount,
        )

        (
            buy_balance_amount_atomic,
            buy_decimals,
        ) = await self.chain.convert_amount_to_amount_atomic(
            token=buy_balance.asset.get_pricing_token(),
            amount_readable=buy_balance.amount,
        )

        if isinstance(buy_balance.asset, Basket) and isinstance(
            sell_balance.asset, Token
        ):
            return await self.__build_steps_for_buy_basket(
                buy_balance=BalanceAtomic(
                    asset=buy_balance.asset,
                    amount=buy_balance.amount,
                    amount_atomic=buy_balance_amount_atomic,
                    decimals=buy_decimals,
                ),
                sell_balance=BalanceAtomic(
                    asset=sell_balance.asset,
                    amount=sell_balance.amount,
                    amount_atomic=sell_balance_amount_atomic,
                    decimals=sell_balance_decimals,
                ),
            )
        if isinstance(sell_balance.asset, Basket) and isinstance(
            buy_balance.asset, Token
        ):
            return await self.__build_steps_for_sell_basket(
                buy_balance=BalanceAtomic(
                    asset=buy_balance.asset,
                    amount=buy_balance.amount,
                    amount_atomic=buy_balance_amount_atomic,
                    decimals=buy_decimals,
                ),
                sell_balance=BalanceAtomic(
                    asset=sell_balance.asset,
                    amount=sell_balance.amount,
                    amount_atomic=sell_balance_amount_atomic,
                    decimals=sell_balance_decimals,
                ),
            )
        if isinstance(sell_balance.asset, Token) and isinstance(
            buy_balance.asset, Token
        ):
            (
                buy_balance_amount_atomic,
                buy_decimals,
            ) = await self.chain.convert_amount_to_amount_atomic(
                token=buy_balance.asset, amount_readable=buy_balance.amount
            )
            (
                sell_balance_amount_atomic,
                sell_decimals,
            ) = await self.chain.convert_amount_to_amount_atomic(
                token=sell_balance.asset, amount_readable=sell_balance.amount
            )

            return [
                PricedInvestmentStep(
                    id=self.id_generator.generate_random_id(),
                    asset_type="TOKEN",
                    sell_balance=BalanceAtomic(
                        asset=sell_balance.asset,
                        amount=sell_balance.amount,
                        amount_atomic=sell_balance_amount_atomic,
                        decimals=sell_decimals,
                    ),
                    buy_balance=BalanceAtomic(
                        asset=buy_balance.asset,
                        amount=buy_balance.amount,
                        amount_atomic=buy_balance_amount_atomic,
                        decimals=buy_decimals,
                    ),
                )
            ]
        return []

    async def __build_steps_for_buy_basket(
        self, buy_balance: BalanceAtomic[Basket], sell_balance: BalanceAtomic[Token]
    ) -> list[PricedInvestmentStep]:
        parent_id = self.id_generator.generate_random_id()

        tasks = [
            self.exchange.convert_balance_to_token(
                balance=self.__compute_token_balance_with_basket_weight(
                    buy_balance.asset, sell_balance
                ),
                token=token,
                investment_parameters=investment_parameters,
            )
            for token in buy_balance.asset.tokens
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        priced_basket_steps: list[PricedInvestmentStep] = [
            PricedInvestmentStep(
                id=parent_id,
                asset_type="BASKET",
                sell_balance=sell_balance,
                buy_balance=buy_balance,
                basket_id=buy_balance.asset.id,
            )
        ]

        for i, result in enumerate(results):
            if isinstance(result, BaseException):
                print(f"price Investment Plan step {i} failed: {result!r}")
            else:
                priced_basket_steps.append(
                    PricedInvestmentStep(
                        id=self.id_generator.generate_random_id(),
                        asset_type="TOKEN",
                        sell_balance=result.sell_balance,
                        buy_balance=result.buy_balance,
                        basket_id=buy_balance.asset.id,
                        parent_id=parent_id,
                    )
                )

        return priced_basket_steps

    async def __build_steps_for_sell_basket(
        self, sell_balance: BalanceAtomic[Basket], buy_balance: BalanceAtomic[Token]
    ) -> list[PricedInvestmentStep]:
        parent_id = self.id_generator.generate_random_id()

        tasks = [
            self.exchange.convert_balance_to_token(
                # TODO: Handle selling basket
                balance=BalanceAtomic(
                    asset=token, amount=Decimal("0"), amount_atomic=0, decimals=18
                ),
                token=buy_balance.asset,
                investment_parameters=investment_parameters,
            )
            for token in sell_balance.asset.tokens
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        priced_basket_steps: list[PricedInvestmentStep] = [
            PricedInvestmentStep(
                id=parent_id,
                asset_type="BASKET",
                sell_balance=sell_balance,
                buy_balance=buy_balance,
                basket_id=sell_balance.asset.id,
            )
        ]

        for i, result in enumerate(results):
            if isinstance(result, BaseException):
                print(f"price Investment Plan step {i} failed: {result!r}")
            else:
                priced_basket_steps.append(
                    PricedInvestmentStep(
                        id=self.id_generator.generate_random_id(),
                        asset_type="TOKEN",
                        sell_balance=result.sell_balance,
                        buy_balance=result.buy_balance,
                        basket_id=sell_balance.asset.id,
                        parent_id=parent_id,
                    )
                )

        return priced_basket_steps

    def __compute_token_balance_with_basket_weight(
        self, basket: Basket, balance: BalanceAtomic[Token]
    ) -> BalanceAtomic[Token]:
        basket_token_length = len(basket.tokens)

        return BalanceAtomic(
            asset=balance.asset,
            amount=balance.amount / basket_token_length,
            amount_atomic=int(
                Decimal(balance.amount_atomic / basket_token_length).to_integral_exact(
                    rounding=ROUND_DOWN
                )
            ),
            decimals=balance.decimals,
        )

    async def _assert_has_sufficient_balances(
        self, priced_investment_plan: PricedInvestmentPlan
    ):
        holding_balances_per_token = await self._get_all_holding_balances()

        for step_matrix in priced_investment_plan.steps:
            # Give priority to basket orders to avoid insufficient balance errors
            basket_order = next(
                (step for step in step_matrix if step.asset_type == "BASKET"), None
            )

            # Only basket orders will have several steps
            step = basket_order if basket_order else step_matrix[0]

            if step.sell_balance.asset.id not in holding_balances_per_token:
                raise InsufficientAssetBalance(step.sell_balance.asset)

            holding_balances_per_token[
                step.sell_balance.asset.id
            ].amount -= step.sell_balance.amount

            if holding_balances_per_token[step.sell_balance.asset.id].amount < 0:
                raise InsufficientAssetBalance(step.sell_balance.asset)

    async def _get_all_holding_balances(self) -> dict[str, BalanceAtomic]:
        holdings = await self.posting_repository.get_holding_balances()
        available_balance = await self.chain.get_native_token_balance()

        holding_balances_per_token = {
            balance.asset.id: balance
            for balance in cast(
                list[BalanceAtomic],
                [*[holding.balance for holding in holdings], available_balance],
            )
        }

        return holding_balances_per_token
