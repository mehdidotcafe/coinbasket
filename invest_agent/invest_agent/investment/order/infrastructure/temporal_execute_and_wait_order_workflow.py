import asyncio
from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Awaitable, Callable
from temporalio import workflow
from temporalio.common import RetryPolicy


@dataclass
class OrderRequest:
    id: str


@dataclass
class OrderTryRequest:
    id: str


@dataclass
class OnOrderSuccessRequest:
    id: str
    executed_sell_amount_atomic: int
    executed_buy_amount_atomic: int
    rate: str | None


def plan_activity(name: str, *args: Any, **kwargs: Any) -> Callable[[], Awaitable[Any]]:
    async def _run():
        return await workflow.execute_activity(name, *args, **kwargs)

    return _run


default_start_to_close_timeout = timedelta(seconds=10)
retry_policy = RetryPolicy(maximum_attempts=1)


@workflow.defn
class TemporalExecuteAndWaitOrderWorkflow:
    @workflow.run
    async def run(self, order_request: OrderRequest):
        compensations: list[Callable[[], Awaitable[Any]]] = []
        outputs: list[Any] = []

        print("TemporalExecuteAndWaitOrderWorkflow > run", order_request)

        try:
            order_try_id = await workflow.execute_activity(
                "create_order_try",
                order_request,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(maximum_attempts=3),
            )

            outputs.append({"create_order_try": order_try_id})

            print("TemporalExecuteAndWaitOrderWorkflow > create_order_try", outputs)

            compensations.append(
                plan_activity(
                    "fail_order_try",
                    OrderTryRequest(id=order_try_id),
                    start_to_close_timeout=default_start_to_close_timeout,
                    retry_policy=RetryPolicy(maximum_attempts=3),
                )
            )

            parsed_receipt = await workflow.execute_activity(
                "execute_order_try",
                OrderTryRequest(id=order_try_id),
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry_policy,
            )

            outputs.append({"execute_order_try": parsed_receipt})

            print("TemporalExecuteAndWaitOrderWorkflow > execute_order_try", outputs)

            executed_atomic_amounts = await workflow.execute_activity(
                "wait_order_try",
                OrderTryRequest(id=order_try_id),
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(maximum_attempts=5),
            )

            outputs.append({"wait_order_try": executed_atomic_amounts})

            print("TemporalExecuteAndWaitOrderWorkflow > wait_order_try", outputs)

            transaction_id = await workflow.execute_activity(
                "on_order_success",
                OnOrderSuccessRequest(
                    id=order_request.id,
                    executed_sell_amount_atomic=executed_atomic_amounts[
                        "executed_sell_amount_atomic"
                    ],
                    executed_buy_amount_atomic=executed_atomic_amounts[
                        "executed_buy_amount_atomic"
                    ],
                    rate=executed_atomic_amounts["rate"],
                ),
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(maximum_attempts=3),
            )

            outputs.append({"on_order_success": transaction_id})

            print("TemporalExecuteAndWaitOrderWorkflow > on_order_success", outputs)

            return transaction_id
        except Exception as e:
            print(
                "TemporalExecuteAndWaitOrderWorkflow > Exception in workflow:", str(e)
            )
            compensation_results = await asyncio.gather(
                *[c() for c in compensations], return_exceptions=True
            )

            outputs.append(
                {"compensation_results": [str(r) for r in compensation_results]}
            )
            raise e
