from decimal import Decimal
from unittest import mock
from pytest import fixture
from api.investment.order.order_repository import OrderRepository
from api.investment.order.task.order_on_order_success_task import (
    OnOrderSuccessTask,
)
from api.investment.order.task.order_submitter_tasks import (
    EventuallySetParentOrderToSuccessTask,
)
from api.investment.order.order import Order
from api.investment.transaction.transaction import Transaction
from api.chain.chain import BalanceAtomic
from api.protocol.fixture.basket import big4_basket
from api.protocol.fixture.token import bnb_token, sol_token, eth_token
from api.chain.chain import ParsedReceipt


@fixture
def order_repository():
    return mock.Mock(spec=OrderRepository)


@fixture
def on_order_success():
    return mock.Mock(spec=OnOrderSuccessTask)


@fixture
def transactions():
    return [
        Transaction(
            id="tx1",
            order_id="order1",
            created_at=0,
            sell_balance=BalanceAtomic(
                amount=Decimal("5"), amount_atomic=500, asset=bnb_token, decimals=3
            ),
            buy_balance=BalanceAtomic(
                amount=Decimal("10"), amount_atomic=1000, asset=sol_token, decimals=3
            ),
            executed_sell_balance=BalanceAtomic(
                amount=Decimal("5"), amount_atomic=500, asset=bnb_token, decimals=3
            ),
            executed_buy_balance=BalanceAtomic(
                amount=Decimal("9"), amount_atomic=900, asset=sol_token, decimals=3
            ),
            type="BUY",
            trigger="MANUAL",
            asset_type="TOKEN",
        ),
        Transaction(
            id="tx2",
            order_id="order2",
            created_at=0,
            sell_balance=BalanceAtomic(
                amount=Decimal("5"), amount_atomic=500, asset=bnb_token, decimals=3
            ),
            buy_balance=BalanceAtomic(
                amount=Decimal("200"), amount_atomic=20000, asset=eth_token, decimals=3
            ),
            executed_sell_balance=BalanceAtomic(
                amount=Decimal("5"), amount_atomic=500, asset=bnb_token, decimals=3
            ),
            executed_buy_balance=BalanceAtomic(
                amount=Decimal("100"), amount_atomic=10000, asset=eth_token, decimals=3
            ),
            type="BUY",
            trigger="MANUAL",
            asset_type="TOKEN",
        ),
    ]


async def test_eventually_set_parent_order_to_success_task_without_parent_order(
    order_repository: OrderRepository,
    on_order_success: OnOrderSuccessTask,
    transactions: list[Transaction],
):
    task = EventuallySetParentOrderToSuccessTask(order_repository, on_order_success)

    result = await task.execute(transactions, None)

    on_order_success.execute.assert_not_called()

    assert result is None


async def test_eventually_set_parent_order_to_success_task_with_parent_order(
    order_repository: OrderRepository,
    on_order_success: OnOrderSuccessTask,
    transactions: list[Transaction],
):
    task = EventuallySetParentOrderToSuccessTask(order_repository, on_order_success)

    parent_order = Order(
        id="parent_order_id",
        sell_balance=BalanceAtomic(
            amount=Decimal("1"), amount_atomic=1000, asset=bnb_token, decimals=3
        ),
        buy_balance=BalanceAtomic(
            amount=Decimal("2"), amount_atomic=2000, asset=big4_basket, decimals=3
        ),
        type="BUY",
        asset_type="TOKEN",
        tries=[],
        created_at=0,
        status="PENDING",
        trigger="MANUAL",
    )

    await task.execute(transactions, parent_order)

    on_order_success.execute.assert_called_once_with(
        order=parent_order,
        order_try=None,
        parsed_receipt=ParsedReceipt(
            executed_sell_balance=parent_order.sell_balance,
            executed_buy_balance=BalanceAtomic(
                amount=Decimal("1"), amount_atomic=1000, asset=big4_basket, decimals=3
            ),
            rate=Decimal(
                (
                    parent_order.buy_balance
                    / BalanceAtomic(
                        amount=Decimal("1"),
                        amount_atomic=1000,
                        asset=big4_basket,
                        decimals=3,
                    )
                ).amount_atomic
            ),
        ),
    )
