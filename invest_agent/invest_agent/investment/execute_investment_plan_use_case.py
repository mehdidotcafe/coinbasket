import asyncio
from dataclasses import dataclass
from decimal import ROUND_DOWN, Decimal
import itertools
from typing import cast
from invest_agent.chain.balance import Balance, BalanceAtomic
from invest_agent.chain.chain import Chain
from invest_agent.datetime.date_time import DateTime
from invest_agent.investment.exception.cannot_swap_basket_for_another_exception import (
    CannotSwapBasketForAnotherException,
)
from invest_agent.investment.exchange.exchange import Exchange
from invest_agent.investment.investment_parameters import InvestmentParameters
from invest_agent.investment.investment_planner.investment_plan import (
    InvestmentPlan,
    InvestmentPlanStep,
)
from invest_agent.investment.order.order import Order
from invest_agent.investment.order.order_submitter import OrderSubmitter
from protocol.basket import Basket
from protocol.token import Token
from shared.id_generator.id_generator import IdGenerator


@dataclass
class FlattenedInvestmentStep:
    sell_balance: BalanceAtomic[Token]
    buy_balance: BalanceAtomic[Token]
    basket_id: str | None = None


@dataclass
class FlattenedInvestmentPlan:
    steps: list[FlattenedInvestmentStep]


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
    ):
        self.id_generator = id_generator
        self.date_time = date_time
        self.chain = chain
        self.order_submitter = order_submitter
        self.exchange = exchange

    async def execute(self, investment_plan: InvestmentPlan) -> list[Order]:
        """Swap assets.

        Args:
            investment_plan: The investment plan to execute.
        Returns:
            A list of Orders created for the assets in the investment plan.
        """
        flattened_investment_plan = await self.__flatten_investment_plan(
            investment_plan
        )

        orders = list(
            itertools.chain.from_iterable(
                [
                    self.__map_flattened_investment_plan_step_to_orders(step)
                    for step in flattened_investment_plan.steps
                ]
            )
        )

        return await self.order_submitter.submit_orders(orders)

    def __map_flattened_investment_plan_step_to_orders(
        self, step: FlattenedInvestmentStep
    ) -> list[Order]:
        return [
            Order(
                id=self.id_generator.generate_random_id(),
                sell_balance=step.sell_balance,
                buy_balance=step.buy_balance,
                type=self.__get_order_type(
                    step.sell_balance.asset, step.buy_balance.asset
                ),
                tries=[],
                created_at=self.date_time.now(),
                status="PENDING",
                trigger="MANUAL",
                basket_id=step.basket_id,
            )
        ]

    def __get_order_type(self, sell_token: Token, buy_token: Token):
        native_token = self.chain.get_base_token()

        if sell_token == native_token:
            return "BUY"
        if buy_token == native_token:
            return "SELL"
        return "SWAP"

    async def __flatten_investment_plan(
        self, investment_plan: InvestmentPlan
    ) -> FlattenedInvestmentPlan:
        steps: list[FlattenedInvestmentStep] = []

        # TODO: Make async
        for step in investment_plan.steps:
            flattened_step = await self.__flatten_investment_plan_step(step)
            steps.extend(flattened_step)

        return FlattenedInvestmentPlan(steps)

    async def __flatten_investment_plan_step(
        self, step: InvestmentPlanStep
    ) -> list[FlattenedInvestmentStep]:
        buy_balance = step.buy_balance
        sell_balance = step.sell_balance

        if isinstance(buy_balance.asset, Basket) and isinstance(
            sell_balance.asset, Basket
        ):
            raise CannotSwapBasketForAnotherException()

        if isinstance(buy_balance.asset, Basket) and isinstance(
            sell_balance.asset, Token
        ):
            sell_balance_amount_atomic = (
                await self.chain.convert_amount_to_amount_atomic(
                    token=sell_balance.asset, amount_readable=sell_balance.amount
                )
            )

            return await self.__build_steps_for_buy_basket(
                buy_balance=cast(Balance[Basket], buy_balance),
                sell_balance=BalanceAtomic(
                    asset=sell_balance.asset,
                    amount=sell_balance.amount,
                    amount_atomic=sell_balance_amount_atomic,
                ),
            )
        if isinstance(sell_balance.asset, Basket) and isinstance(
            buy_balance.asset, Token
        ):
            return await self.__build_steps_for_sell_basket(
                sell_balance=cast(Balance[Basket], sell_balance),
                buy_balance=cast(Balance[Token], buy_balance),
            )
        if isinstance(sell_balance.asset, Token) and isinstance(
            buy_balance.asset, Token
        ):
            buy_balance_amount_atomic = (
                await self.chain.convert_amount_to_amount_atomic(
                    token=buy_balance.asset, amount_readable=buy_balance.amount
                )
            )
            sell_balance_amount_atomic = (
                await self.chain.convert_amount_to_amount_atomic(
                    token=sell_balance.asset, amount_readable=sell_balance.amount
                )
            )

            return [
                FlattenedInvestmentStep(
                    sell_balance=BalanceAtomic(
                        asset=sell_balance.asset,
                        amount=sell_balance.amount,
                        amount_atomic=sell_balance_amount_atomic,
                    ),
                    buy_balance=BalanceAtomic(
                        asset=buy_balance.asset,
                        amount=buy_balance.amount,
                        amount_atomic=buy_balance_amount_atomic,
                    ),
                )
            ]
        return []

    async def __build_steps_for_buy_basket(
        self, buy_balance: Balance[Basket], sell_balance: BalanceAtomic[Token]
    ) -> list[FlattenedInvestmentStep]:
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

        flattened_basket_steps: list[FlattenedInvestmentStep] = []

        for i, result in enumerate(results):
            if isinstance(result, BaseException):
                print(f"Flatten Investment Plan step {i} failed: {result!r}")
            else:
                flattened_basket_steps.append(
                    # TODO: Store basket info
                    FlattenedInvestmentStep(
                        sell_balance=result.sell_balance,
                        buy_balance=result.buy_balance,
                        basket_id=buy_balance.asset.id,
                    )
                )

        return flattened_basket_steps

    async def __build_steps_for_sell_basket(
        self, sell_balance: Balance[Basket], buy_balance: Balance[Token]
    ) -> list[FlattenedInvestmentStep]:
        tasks = [
            self.exchange.convert_balance_to_token(
                # TODO: Handle selling basket
                balance=BalanceAtomic(
                    asset=token, amount=Decimal("0"), amount_atomic=0
                ),
                token=buy_balance.asset,
                investment_parameters=investment_parameters,
            )
            for token in sell_balance.asset.tokens
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        flattened_basket_steps: list[FlattenedInvestmentStep] = []

        for i, result in enumerate(results):
            if isinstance(result, BaseException):
                print(f"Flatten Investment Plan step {i} failed: {result!r}")
            else:
                # TODO: Store basket info
                flattened_basket_steps.append(
                    FlattenedInvestmentStep(
                        sell_balance=result.sell_balance,
                        buy_balance=result.buy_balance,
                        basket_id=sell_balance.asset.id,
                    )
                )

        return flattened_basket_steps

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
        )
