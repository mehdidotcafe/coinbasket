from dataclasses import dataclass
from invest_agent.investment.order.task.order_on_order_success_task import (
    OnOrderSuccessTask,
)
from invest_agent.investment.order.task.execute_and_wait_order_tasks import (
    CreateOrderTryTask,
    ExecuteOrderTryTask,
    WaitOrderTryTask,
    FailOrderTryTask,
)
from invest_agent.registry import (
    exchange,
    chain,
    id_generator,
    date_time,
    random_generator,
    order_repository,
    configuration,
    posting_repository,
    transaction_repository,
    session_manager,
)
from temporalio import activity


@dataclass
class OrderRequest:
    id: str


@dataclass
class OrderTryRequest:
    id: str


@dataclass
class ExecutedAtomicAmounts:
    executed_sell_amount_atomic: int
    executed_buy_amount_atomic: int
    rate: str | None


on_order_success_task = OnOrderSuccessTask(
    order_repository,
    transaction_repository,
    posting_repository,
    chain,
    date_time,
    session_manager,
)
create_order_try_task = CreateOrderTryTask(
    order_repository,
    exchange,
    chain,
    id_generator,
    date_time,
    configuration={"environment": configuration.agent_env},
)
execute_order_try_task = ExecuteOrderTryTask(
    order_repository,
    exchange,
    chain,
    id_generator,
    date_time,
    random_generator,
    configuration={"environment": configuration.agent_env},
)
wait_order_try_task = WaitOrderTryTask(
    order_repository,
    exchange,
    chain,
    id_generator,
    date_time,
    random_generator,
    configuration={"environment": configuration.agent_env},
)
fail_order_try_task = FailOrderTryTask(order_repository, date_time)


@activity.defn(name="create_order_try")
async def create_order_try(order_request: OrderRequest):
    print("Activity: create_order_try", order_request)

    order = await order_repository.get_order(order_request.id)
    if not order:
        raise Exception(f"Order {order_request.id} not found")

    order_try = await create_order_try_task.execute(order)

    return order_try.id


@activity.defn(name="execute_order_try")
async def execute_order_try(order_try_request: OrderTryRequest):
    print("Activity: execute_order_try", order_try_request)

    order_try = await order_repository.get_order_try(order_try_request.id)
    if not order_try:
        raise Exception(f"OrderTry {order_try_request.id} not found")

    return await execute_order_try_task.execute(order_try)


@activity.defn(name="wait_order_try")
async def wait_order_try(order_try_request: OrderTryRequest):
    print("Activity: wait_order_try", order_try_request)

    order_try = await order_repository.get_order_try(order_try_request.id)
    if not order_try:
        raise Exception(f"OrderTry {order_try_request.id} not found")

    order = await order_repository.get_order(order_try.order_id)
    if not order:
        raise Exception(f"Order {order_try.order_id} not found")

    result = await wait_order_try_task.execute(order, order_try)

    if not result:
        raise Exception(f"OrderTry {order_try.id} execution failed")

    return ExecutedAtomicAmounts(
        executed_sell_amount_atomic=result.executed_sell_balance.amount_atomic,
        executed_buy_amount_atomic=result.executed_buy_balance.amount_atomic,
        rate=str(result.rate) if result.rate else None,
    )


@activity.defn(name="fail_order_try")
async def fail_order_try(order_try_request: OrderTryRequest):
    print("Activity: fail_order_try", order_try_request)

    order_try = await order_repository.get_order_try(order_try_request.id)
    if not order_try:
        raise Exception(f"OrderTry {order_try_request.id} not found")

    return await fail_order_try_task.execute(order_try)


@activity.defn(name="is_internal_order")
async def is_internal_order(order_request: OrderRequest):
    print("Activity: is_internal_order", order_request)

    order = await order_repository.get_order(order_request.id)
    if not order:
        raise Exception(f"Order {order_request.id} not found")

    return order.buy_balance.asset == order.sell_balance.asset


@activity.defn(name="get_order_balances_atomic")
async def get_order_balances_atomic(order_request: OrderRequest):
    print("Activity: get_order_balances_atomic", order_request)

    order = await order_repository.get_order(order_request.id)
    if not order:
        raise Exception(f"Order {order_request.id} not found")

    return ExecutedAtomicAmounts(
        executed_sell_amount_atomic=order.sell_balance.amount_atomic,
        executed_buy_amount_atomic=order.buy_balance.amount_atomic,
        rate=str(order.buy_balance.amount_atomic / order.sell_balance.amount_atomic)
        if order.sell_balance.amount_atomic > 0
        else "0",
    )
