import asyncio
from invest_agent.investment.order.infrastructure.temporal_execute_and_wait_order_workflow import (
    TemporalExecuteAndWaitOrderWorkflow,
)
from temporalio.client import Client
from temporalio.worker import Worker
from invest_agent.investment.order.infrastructure.temporal_order_submitter_workflow import (
    TemporalOrderSubmitterWorkflow,
)
from invest_agent.investment.order.infrastructure.temporal_order_submitter_activities import (
    fail_order,
    revert_succeeded_orders,
    eventually_fail_parent_order,
    eventually_revert_order_leftovers,
    eventually_success_parent_order,
    on_order_success,
)
from invest_agent.investment.order.infrastructure.temporal_execute_and_wait_order_activities import (
    create_order_try,
    execute_order_try,
    wait_order_try,
    fail_order_try,
)
from invest_agent.registry import (
    configuration,
)


async def main():
    agent_name = configuration.agent_name
    client = await Client.connect(
        f"{configuration.temporal_host}:{configuration.temporal_port}"
    )
    worker = Worker(
        client,
        task_queue=f"order-submitter-workflow-{agent_name}",
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
        ],
    )
    print(f"{agent_name} worker started.")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
