from dataclasses import dataclass
from decimal import Decimal
from typing import Literal, TypedDict
from invest_agent.chain.balance import BalanceAtomic
from invest_agent.chain.chain import ParsedReceipt
from invest_agent.investment.order.task.order_on_order_success_task import (
    OnOrderSuccessTask,
)
from invest_agent.investment.order.task.order_submitter_tasks import (
    EventuallySetParentOrderToFailTask,
    EventuallySetParentOrderToSuccessTask,
    RevertOrderLeftoverTask,
    RevertSucceededOrderTask,
)
from invest_agent.registry import (
    chain,
    date_time,
    order_repository,
    posting_repository,
    transaction_repository,
    session_manager,
)
from temporalio import activity


@dataclass
class OrderRequest:
    id: str


@dataclass
class OnOrderSuccessRequest:
    id: str
    executed_sell_amount_atomic: int
    executed_buy_amount_atomic: int
    rate: str | None


@dataclass
class EventuallySuccessParentOrderRequest:
    transaction_ids: list[str]
    order_ids: list[str]


class TaskConfiguration(TypedDict):
    environment: Literal["development", "production", "test"]


on_order_success_task = OnOrderSuccessTask(
    order_repository,
    transaction_repository,
    posting_repository,
    chain,
    date_time,
    session_manager,
)

revert_succeeded_order_task = RevertSucceededOrderTask(order_repository)
revert_order_leftover_task = RevertOrderLeftoverTask(order_repository)
eventually_set_parent_order_to_fail_task = EventuallySetParentOrderToFailTask(
    order_repository
)
eventually_set_parent_order_to_success_task = EventuallySetParentOrderToSuccessTask(
    order_repository, on_order_success_task
)


# Compensation
@activity.defn(name="fail_order")
async def fail_order(order_request: OrderRequest) -> bool:
    await order_repository.set_order_to_fail(order_request.id)
    return True


# Compensation
@activity.defn(name="revert_succeeded_orders")
async def revert_succeeded_orders(order_requests: list[OrderRequest]) -> bool:
    print(f"Revert succeeded orders: {[o.id for o in order_requests]}")
    return True


# Compensation
@activity.defn(name="eventually_fail_parent_order")
async def eventually_fail_parent_order(order_request: OrderRequest) -> bool:
    order = await order_repository.get_order(order_request.id)
    if not order:
        raise Exception(f"Order {order_request.id} not found")
    parent_order = (
        await order_repository.get_order(order.parent_order_id)
        if order.parent_order_id
        else None
    )

    if parent_order:
        await order_repository.set_order_to_fail(parent_order.id)
    return True


@activity.defn(name="eventually_revert_order_leftovers")
async def eventually_revert_order_leftovers(order_requests: list[OrderRequest]) -> bool:
    print("Eventually revert leftovers")
    return True


@activity.defn(name="on_order_success")
async def on_order_success(request: OnOrderSuccessRequest):
    order = await order_repository.get_order(request.id)
    if not order:
        raise Exception(f"Order {request.id} not found")

    transaction = await on_order_success_task.execute(
        order,
        order.tries[-1] if order.tries else None,
        ParsedReceipt(
            executed_sell_balance=BalanceAtomic(
                asset=order.sell_balance.asset,
                amount_atomic=request.executed_sell_amount_atomic,
                amount=Decimal(request.executed_sell_amount_atomic)
                / (10**order.sell_balance.decimals),
                decimals=order.sell_balance.decimals,
            ),
            executed_buy_balance=BalanceAtomic(
                asset=order.buy_balance.asset,
                amount_atomic=request.executed_buy_amount_atomic,
                amount=Decimal(request.executed_buy_amount_atomic)
                / (10**order.buy_balance.decimals),
                decimals=order.buy_balance.decimals,
            ),
            rate=Decimal(request.rate) if request.rate else None,
        ),
    )
    return transaction.id


@activity.defn(name="eventually_success_parent_order")
async def eventually_success_parent_order(
    request: EventuallySuccessParentOrderRequest,
) -> bool:
    transactions = await transaction_repository.get_transactions(
        transaction_ids=request.transaction_ids
    )
    first_order = await order_repository.get_order(request.order_ids[0])

    parent_order = (
        await order_repository.get_order(first_order.parent_order_id)
        if first_order and first_order.parent_order_id
        else None
    )

    if not transactions:
        raise Exception("Transactions not found")

    await eventually_set_parent_order_to_success_task.execute(
        transactions=transactions, parent_order=parent_order
    )
    return True
