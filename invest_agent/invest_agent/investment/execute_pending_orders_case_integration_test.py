from asyncio import sleep
from decimal import Decimal
from typing import Any
from invest_agent.chain.balance import Balance
from invest_agent.investment.order.order import ChainTransaction, Order, Try
from pytest import fixture
from sqlalchemy import select

from invest_agent.main import execute_pending_orders_use_case
from invest_agent.investment.order.infrastructure.sql_alchemy_order_repository import (
    OrderModel,
    OrderTryChainTransactionModel,
)
from invest_agent.investment.transaction.infrastructure.sql_alchemy_transaction_repository import (
    TransactionModel,
)
from invest_agent.investment.order.infrastructure.sql_alchemy_order_repository import (
    OrderTryModel,
)
from protocol.fixture.token import bnb_token, eth_token, usdt_token, sol_token

from invest_agent.test.database.make_session import make_session
from invest_agent.test.database.cleanup_all import cleanup_all


@fixture
def current_orders_no_try():
    return [
        Order(
            id="641763c2-41e2-4af0-936f-32c1a84499c1",
            sell_balance=Balance(token=bnb_token, amount=Decimal(1)),
            buy_balance=Balance(token=eth_token, amount=Decimal(0.1)),
            type="BUY",
            created_at=1939494,
            status="PENDING",
            trigger="MANUAL",
            basket_id=None,
            tries=[],
        ),
        Order(
            id="641763c2-41e2-4af0-936f-32c1a84499c2",
            sell_balance=Balance(token=bnb_token, amount=Decimal(1)),
            buy_balance=Balance(token=usdt_token, amount=Decimal(0.1)),
            type="BUY",
            created_at=1939494,
            status="SUCCESS",
            trigger="MANUAL",
            basket_id=None,
            tries=[],
        ),
        Order(
            id="641763c2-41e2-4af0-936f-32c1a84499c3",
            sell_balance=Balance(token=bnb_token, amount=Decimal(1)),
            buy_balance=Balance(token=sol_token, amount=Decimal(0.1)),
            type="BUY",
            created_at=1939494,
            status="FAIL",
            trigger="MANUAL",
            basket_id=None,
            tries=[],
        ),
    ]


@fixture(scope="function")
async def seed_orders_no_try(current_orders_no_try: list[Order]):
    async with make_session() as session:
        async with session.begin():
            for order in current_orders_no_try:
                order_model = OrderModel(
                    id=order.id,
                    sell_balance=order.sell_balance.serialize(),
                    buy_balance=order.buy_balance.serialize(),
                    type=order.type,
                    created_at=order.created_at,
                    status=order.status,
                    trigger=order.trigger,
                    basket_id=order.basket_id,
                )
                session.add(order_model)

    yield current_orders_no_try


@fixture
def current_orders_tries():
    return [
        Order(
            id="641763c2-41e2-4af0-936f-32c1a84499c1",
            sell_balance=Balance(token=bnb_token, amount=Decimal(1)),
            buy_balance=Balance(token=eth_token, amount=Decimal(0.1)),
            type="BUY",
            created_at=1939494,
            status="PENDING",
            trigger="MANUAL",
            basket_id=None,
            tries=[
                Try(
                    id="try1",
                    order_id="641763c2-41e2-4af0-936f-32c1a84499c1",
                    created_at=1939494,
                    provider="provider1",
                    buy_balance=Balance(token=eth_token, amount=Decimal(0.1)),
                    fees=None,
                    chain_transactions=[
                        ChainTransaction(
                            id="chain_tx1",
                            try_id="try1",
                            order_id="641763c2-41e2-4af0-936f-32c1a84499c1",
                            type="SEND",
                            data="data1",
                            hash="0xba08280c3d63edd24523905fb04725c13b69a0f62dd8abe8ac33f31772b6565e",
                            status="PENDING",
                        )
                    ],
                )
            ],
        ),
        Order(
            id="641763c2-41e2-4af0-936f-32c1a84499c2",
            sell_balance=Balance(token=bnb_token, amount=Decimal(1)),
            buy_balance=Balance(token=usdt_token, amount=Decimal(0.1)),
            type="BUY",
            created_at=1939494,
            status="PENDING",
            trigger="MANUAL",
            basket_id=None,
            tries=[
                Try(
                    id="try2",
                    order_id="641763c2-41e2-4af0-936f-32c1a84499c2",
                    created_at=1939494,
                    provider="provider2",
                    buy_balance=Balance(token=usdt_token, amount=Decimal(0.1)),
                    fees=None,
                    chain_transactions=[
                        ChainTransaction(
                            id="chain_tx2",
                            try_id="try2",
                            order_id="641763c2-41e2-4af0-936f-32c1a84499c2",
                            type="SEND",
                            data="data2",
                            hash="0xba08280c3d63edd24523905fb04725c13b69a0f62dd8abe8ac33f31772b6565e",
                            status="FAIL",
                        )
                    ],
                )
            ],
        ),
        Order(
            id="641763c2-41e2-4af0-936f-32c1a84499c3",
            sell_balance=Balance(token=bnb_token, amount=Decimal(1)),
            buy_balance=Balance(token=sol_token, amount=Decimal(0.1)),
            type="BUY",
            created_at=1939494,
            status="PENDING",
            trigger="MANUAL",
            basket_id=None,
            tries=[
                Try(
                    id="try3",
                    order_id="641763c2-41e2-4af0-936f-32c1a84499c3",
                    created_at=1939494,
                    provider="provider3",
                    buy_balance=Balance(token=usdt_token, amount=Decimal(0.1)),
                    fees=None,
                    chain_transactions=[],
                )
            ],
        ),
    ]


@fixture(scope="function")
async def seed_orders_tries(current_orders_tries: list[Order]):
    async with make_session() as session:
        async with session.begin():
            for order in current_orders_tries:
                order_model = OrderModel(
                    id=order.id,
                    sell_balance=order.sell_balance.serialize(),
                    buy_balance=order.buy_balance.serialize(),
                    type=order.type,
                    created_at=order.created_at,
                    status=order.status,
                    trigger=order.trigger,
                    basket_id=order.basket_id,
                )
                session.add(order_model)

                for order_try in order.tries:
                    try_model = OrderTryModel(
                        id=order_try.id,
                        order_id=order.id,
                        created_at=order_try.created_at,
                        provider=order_try.provider,
                        buy_balance=order_try.buy_balance.serialize(),
                        fees=order_try.fees,
                    )
                    session.add(try_model)

                    for chain_transaction in order_try.chain_transactions:
                        chain_tx_model = OrderTryChainTransactionModel(
                            id=chain_transaction.id,
                            try_id=chain_transaction.try_id,
                            order_id=chain_transaction.order_id,
                            type=chain_transaction.type,
                            data=chain_transaction.data,
                            hash=chain_transaction.hash,
                            status=chain_transaction.status,
                        )
                        session.add(chain_tx_model)

    yield current_orders_tries


async def fetch_order_by_id(id: str):
    async with make_session() as session:
        result = await session.execute(select(OrderModel).where(OrderModel.id == id))
        row = result.scalar_one_or_none()
        return row


async def fetch_all_orders():
    async with make_session() as session:
        result = await session.execute(select(OrderModel))
        rows = result.scalars().all()
        return rows


async def fetch_order_tries_by_order_id(order_id: str):
    async with make_session() as session:
        result = await session.execute(
            select(OrderTryModel).where(OrderTryModel.order_id == order_id)
        )
        rows = result.scalars().all()
        return rows


async def fetch_chain_transaction_by_id(chain_transaction_id: str):
    async with make_session() as session:
        result = await session.execute(
            select(OrderTryChainTransactionModel).where(
                OrderTryChainTransactionModel.id == chain_transaction_id
            )
        )
        row = result.scalar_one_or_none()
        return row


async def fetch_chain_transactions_by_try_id(try_id: str):
    async with make_session() as session:
        result = await session.execute(
            select(OrderTryChainTransactionModel).where(
                OrderTryChainTransactionModel.try_id == try_id
            )
        )
        row = result.scalars().all()
        return row


async def fetch_transaction_by_order_id(order_id: str):
    async with make_session() as session:
        result = await session.execute(
            select(TransactionModel).where(TransactionModel.order_id == order_id)
        )
        rows = result.scalars().all()
        return rows


async def wait_for_orders():
    await sleep(60)


async def test_integration_execute_pending_orders_use_case_no_try(
    seed_orders_no_try: Any,
    cleanup_all: Any,
):
    await execute_pending_orders_use_case.execute()

    await wait_for_orders()

    order = await fetch_order_by_id("641763c2-41e2-4af0-936f-32c1a84499c1")
    tries = await fetch_order_tries_by_order_id("641763c2-41e2-4af0-936f-32c1a84499c1")
    transactions = await fetch_transaction_by_order_id(
        "641763c2-41e2-4af0-936f-32c1a84499c1"
    )

    assert order is not None
    assert order.status == "SUCCESS"
    assert len(tries) == 1
    assert len(transactions) == 1


async def test_integration_execute_pending_orders_use_case_with_tries(
    seed_orders_tries: Any,
    cleanup_all: Any,
):
    await execute_pending_orders_use_case.execute()

    await wait_for_orders()

    chain_transaction_1 = await fetch_chain_transaction_by_id("chain_tx1")
    order_1 = await fetch_order_by_id("641763c2-41e2-4af0-936f-32c1a84499c1")

    assert chain_transaction_1 is not None
    assert chain_transaction_1.status == "SUCCESS"
    assert order_1 is not None
    assert order_1.status == "SUCCESS"

    order_2 = await fetch_order_by_id("641763c2-41e2-4af0-936f-32c1a84499c2")
    order_2_tries = await fetch_order_tries_by_order_id(
        "641763c2-41e2-4af0-936f-32c1a84499c2"
    )

    assert len(order_2_tries) == 2

    order_2_try_1_chain_transactions = await fetch_chain_transactions_by_try_id(
        order_2_tries[0].id
    )
    order_2_try_2_chain_transactions = await fetch_chain_transactions_by_try_id(
        order_2_tries[1].id
    )

    assert len(order_2_try_1_chain_transactions) == 1
    assert order_2_try_1_chain_transactions[0].status == "FAIL"

    assert len(order_2_try_2_chain_transactions) == 1
    assert order_2_try_2_chain_transactions[0].status == "SUCCESS"

    assert order_2 is not None
    assert order_2.status == "SUCCESS"

    order_3 = await fetch_order_by_id("641763c2-41e2-4af0-936f-32c1a84499c3")
    order_3_tries = await fetch_order_tries_by_order_id(
        "641763c2-41e2-4af0-936f-32c1a84499c3"
    )

    assert len(order_3_tries) == 2

    order_3_try_1_chain_transactions = await fetch_chain_transactions_by_try_id(
        order_3_tries[0].id
    )
    order_3_try_2_chain_transactions = await fetch_chain_transactions_by_try_id(
        order_3_tries[1].id
    )

    assert len(order_3_try_1_chain_transactions) == 0
    assert len(order_3_try_2_chain_transactions) == 1
    assert order_3_try_2_chain_transactions[0].status == "SUCCESS"

    assert order_3 is not None
    assert order_3.status == "SUCCESS"
