import asyncio
from dataclasses import dataclass
from decimal import Decimal
import itertools
from invest_agent.chain.asset_balance import BasketBalance
from invest_agent.chain.balance import Balance
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
    sell_balance: Balance
    buy_balance: Balance
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

        print(f"Flattened investment plan: {flattened_investment_plan}")

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
                    step.sell_balance.token, step.buy_balance.token
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

        if isinstance(buy_balance, BasketBalance) and isinstance(
            sell_balance, BasketBalance
        ):
            raise CannotSwapBasketForAnotherException()

        if isinstance(buy_balance, BasketBalance) and isinstance(sell_balance, Balance):
            return await self.__build_steps_for_buy_basket(buy_balance, sell_balance)
        if isinstance(sell_balance, BasketBalance) and isinstance(buy_balance, Balance):
            return await self.__build_steps_for_sell_basket(sell_balance, buy_balance)
        if isinstance(sell_balance, Balance) and isinstance(buy_balance, Balance):
            return [
                FlattenedInvestmentStep(
                    sell_balance=sell_balance,
                    buy_balance=buy_balance,
                )
            ]
        return []

    async def __build_steps_for_buy_basket(
        self, buy_balance: BasketBalance, sell_balance: Balance
    ) -> list[FlattenedInvestmentStep]:
        tasks = [
            self.exchange.convert_balance_to_token(
                balance=self.__compute_token_balance_with_basket_weight(
                    buy_balance.basket, sell_balance
                ),
                token=token,
                investment_parameters=investment_parameters,
            )
            for token in buy_balance.basket.tokens
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
                        basket_id=buy_balance.basket.id,
                    )
                )

        return flattened_basket_steps

    async def __build_steps_for_sell_basket(
        self, sell_balance: BasketBalance, buy_balance: Balance
    ) -> list[FlattenedInvestmentStep]:
        tasks = [
            self.exchange.convert_balance_to_token(
                # TODO: Handle selling basket
                balance=Balance(token=token, amount=Decimal("0")),
                token=buy_balance.token,
                investment_parameters=investment_parameters,
            )
            for token in sell_balance.basket.tokens
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
                        basket_id=sell_balance.basket.id,
                    )
                )

        return flattened_basket_steps

    def __compute_token_balance_with_basket_weight(
        self, basket: Basket, balance: Balance
    ) -> Balance:
        print(
            Balance(
                token=balance.token,
                amount=balance.amount / len(basket.tokens),
            )
        )

        return Balance(
            token=balance.token,
            amount=balance.amount / len(basket.tokens),
        )
