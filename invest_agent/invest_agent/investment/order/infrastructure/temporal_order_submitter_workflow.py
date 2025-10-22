import asyncio
from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Awaitable, Callable, Literal, TypedDict, cast
from temporalio import workflow
from temporalio.common import RetryPolicy
from invest_agent.investment.order.infrastructure.temporal_execute_and_wait_order_workflow import (
    TemporalExecuteAndWaitOrderWorkflow,
)


@dataclass
class OrderRequest:
    id: str


@dataclass
class EventuallySuccessParentOrderRequest:
    transaction_ids: list[str]
    order_ids: list[str]


class Configuration(TypedDict):
    environment: Literal["development", "production", "test"]


def plan_activity(name: str, *args: Any, **kwargs: Any) -> Callable[[], Awaitable[Any]]:
    async def _run():
        return await workflow.execute_activity(name, *args, **kwargs)

    return _run


@workflow.defn
class TemporalOrderSubmitterWorkflow:
    @workflow.run
    async def run(self, orders: list[OrderRequest]):
        default_start_to_close_timeout = timedelta(20)
        retry_policy = RetryPolicy(maximum_attempts=5)

        compensations: list[Callable[[], Awaitable[Any]]] = []
        outputs: list[Any] = []

        print("TemporalOrderSubmitterWorkflow > run", orders)

        try:
            execute_and_wait_order_handles = [
                workflow.execute_child_workflow(
                    TemporalExecuteAndWaitOrderWorkflow.run,
                    order,
                    retry_policy=retry_policy,
                    run_timeout=timedelta(minutes=10),
                )
                for order in orders
            ]
            transaction_ids = await asyncio.gather(
                *execute_and_wait_order_handles, return_exceptions=True
            )

            print("TemporalOrderSubmitterWorkflow > execute_and_wait_order", outputs)

            outputs.append(
                {
                    "execute_and_wait_order": [
                        str(transaction_id) for transaction_id in transaction_ids
                    ]
                }
            )

            some_transactions_failed = False
            succeeded_orders: list[OrderRequest] = []
            for order, transaction_id in zip(orders, transaction_ids):
                if isinstance(transaction_id, BaseException):
                    some_transactions_failed = True
                    compensations.append(
                        plan_activity(
                            "fail_order",
                            order,
                            start_to_close_timeout=default_start_to_close_timeout,
                            retry_policy=retry_policy,
                        )
                    )
                else:
                    succeeded_orders.append(order)

            compensations.append(
                plan_activity(
                    "revert_succeeded_orders",
                    succeeded_orders,
                    start_to_close_timeout=default_start_to_close_timeout,
                    retry_policy=retry_policy,
                )
            )

            # Eventually fail parent order
            compensations.append(
                plan_activity(
                    "eventually_fail_parent_order",
                    orders[0],
                    start_to_close_timeout=default_start_to_close_timeout,
                    retry_policy=retry_policy,
                )
            )

            if some_transactions_failed:
                raise BaseException("One or more orders failed")

            eventually_revert_order_leftovers_result = await workflow.execute_activity(
                "eventually_revert_order_leftovers",
                orders,
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=RetryPolicy(maximum_attempts=5),
            )

            outputs.append(
                {
                    "eventually_revert_order_leftovers": eventually_revert_order_leftovers_result
                }
            )

            print(
                "TemporalOrderSubmitterWorkflow > eventually_revert_order_leftovers",
                outputs,
            )

            eventually_success_parent_order_result = await workflow.execute_activity(
                "eventually_success_parent_order",
                EventuallySuccessParentOrderRequest(
                    order_ids=[order.id for order in orders],
                    transaction_ids=cast(list[str], transaction_ids),
                ),
                start_to_close_timeout=default_start_to_close_timeout,
                retry_policy=retry_policy,
            )

            outputs.append(
                {
                    "eventually_success_parent_order": eventually_success_parent_order_result
                }
            )

            print(
                "TemporalOrderSubmitterWorkflow > eventually_success_parent_order",
                outputs,
            )

        except BaseException as e:
            print("TemporalOrderSubmitterWorkflow > Exception in workflow:", e)
            compensation_results = await asyncio.gather(
                *(c() for c in compensations), return_exceptions=True
            )
            outputs.append({"compensation_results": compensation_results})

        print("TemporalOrderSubmitterWorkflow > end", outputs)

        return outputs
