import asyncio
from api.investment.order.infrastructure.temporal_execute_and_wait_order_workflow import (
    TemporalExecuteAndWaitOrderWorkflow,
)
from temporalio.client import Client
from temporalio.worker import Worker
from api.investment.order.infrastructure.temporal_order_submitter_workflow import (
    TemporalOrderSubmitterWorkflow,
)
from api.investment.order.infrastructure.temporal_order_submitter_activities import (
    fail_order,
    revert_succeeded_orders,
    eventually_fail_parent_order,
    eventually_revert_order_leftovers,
    eventually_success_parent_order,
    on_order_success,
)
from api.investment.order.infrastructure.temporal_execute_and_wait_order_activities import (
    create_order_try,
    execute_order_try,
    wait_order_try,
    fail_order_try,
    is_internal_order,
    get_order_balances_atomic,
)
from api.registry import (
    configuration,
)


async def main():
    app_name = configuration.app_name
    client = await Client.connect(
        f"{configuration.temporal_host}:{configuration.temporal_port}"
    )
    worker = Worker(
        client,
        task_queue=f"order-submitter-workflow-{app_name}",
        workflows=[TemporalExecuteAndWaitOrderWorkflow, TemporalOrderSubmitterWorkflow],
        activities=[
            fail_order,
            revert_succeeded_orders,
            eventually_fail_parent_order,
            eventually_revert_order_leftovers,
            eventually_success_parent_order,
            on_order_success,
            create_order_try,
            execute_order_try,
            wait_order_try,
            fail_order_try,
            is_internal_order,
            get_order_balances_atomic,
        ],
    )
    print("Invest Agent Worker Ready.")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
