import itertools
from invest_agent.chain.asset_balance import BasketBalance
from invest_agent.chain.chain import Chain
from invest_agent.datetime.date_time import DateTime
from invest_agent.investment.exception.cannot_swap_basket_for_another_exception import (
    CannotSwapBasketForAnotherException,
)
from invest_agent.investment.investment_planner.investment_plan import (
    InvestmentPlan,
    InvestmentPlanStep,
)
from invest_agent.investment.order.order import Order
from invest_agent.investment.order.order_submitter import OrderSubmitter
from protocol.token import Token
from shared.id_generator.id_generator import IdGenerator


class ExecuteInvestmentPlanUseCase:
    """Use case executing an investment plan."""

    def __init__(
        self,
        id_generator: IdGenerator,
        date_time: DateTime,
        chain: Chain,
        order_submitter: OrderSubmitter,
    ):
        self.id_generator = id_generator
        self.date_time = date_time
        self.chain = chain
        self.order_submitter = order_submitter

    async def execute(self, investment_plan: InvestmentPlan) -> list[Order]:
        """Swap assets.

        Args:
            investment_plan: The investment plan to execute.
        Returns:
            A list of Orders created for the assets in the investment plan.
        """

        orders = list(
            itertools.chain.from_iterable(
                [
                    self.__convert_investment_plan_step_to_orders(step)
                    for step in investment_plan.steps
                ]
            )
        )

        return await self.order_submitter.submit_orders(orders)

    def __convert_investment_plan_step_to_orders(
        self, step: InvestmentPlanStep
    ) -> list[Order]:
        if isinstance(step.buy_balance, BasketBalance) and isinstance(
            step.sell_balance, BasketBalance
        ):
            raise CannotSwapBasketForAnotherException()

        if isinstance(step.buy_balance, BasketBalance):
            return [
                Order(
                    id=self.id_generator.generate_random_id(),
                    sell_balance=balance.sell_balance,
                    buy_balance=balance.buy_balance,
                    type=self.__get_order_type(
                        balance.sell_balance.token, balance.buy_balance.token
                    ),
                    tries=[],
                    created_at=self.date_time.now(),
                    status="PENDING",
                    trigger="MANUAL",
                    basket_id=step.buy_balance.basket.id,
                )
                for balance in step.buy_balance.basket.balances
            ]

        if isinstance(step.sell_balance, BasketBalance):
            return [
                Order(
                    id=self.id_generator.generate_random_id(),
                    sell_balance=balance.sell_balance,
                    buy_balance=balance.buy_balance,
                    type=self.__get_order_type(
                        balance.sell_balance.token, step.buy_balance.token
                    ),
                    tries=[],
                    created_at=self.date_time.now(),
                    status="PENDING",
                    trigger="MANUAL",
                    basket_id=step.sell_balance.basket.id,
                )
                for balance in step.sell_balance.basket.balances
            ]

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
            )
        ]

    def __get_order_type(self, sell_token: Token, buy_token: Token):
        native_token = self.chain.get_base_token()

        if sell_token == native_token:
            return "BUY"
        if buy_token == native_token:
            return "SELL"
        return "SWAP"
