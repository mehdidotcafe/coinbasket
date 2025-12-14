from asyncio import sleep
from decimal import Decimal
from typing import Any
from api.chain.balance import Balance, BalanceAtomic
from api.investment.order.infrastructure.sql_alchemy_order_repository import (
    OrderModel,
)
from api.investment.transaction.infrastructure.sql_alchemy_transaction_repository import (
    TransactionModel,
)
from api.investment.transaction.transaction import Transaction
from api.portfolio.posting.infrastructure.sql_alchemy_posting_repository import (
    PostingModel,
)
from api.portfolio.posting.posting import Posting
from api.investment.order.order import Order
from pytest import fixture, mark

from api.main import (
    execute_investment_plan_use_case,
)
from api.investment.investment_planner.investment_plan import (
    InvestmentPlan,
    InvestmentPlanStep,
)

from protocol.fixture.token import (
    btc_token,
    sol_token,
    usdt_token,
    eth_token,
)
from protocol.fixture.basket import test_basket

from sqlalchemy import select

from api.test.database.make_session import make_session

from api.test.database.cleanup_all import cleanup_all  # noqa: F401
from api.test.database.seed_fixtures import seed_fixtures  # noqa: F401


@fixture
def orders():
    return [
        Order(
            id="f9bd9283-fea4-4e2d-9f3c-4ad0b66503ef",
            sell_balance=BalanceAtomic(
                asset=usdt_token,
                amount=Decimal("100.00"),
                amount_atomic=int(10000 * 10**16),
                decimals=18,
            ),
            buy_balance=BalanceAtomic(
                asset=usdt_token,
                amount=Decimal("100.00"),
                amount_atomic=int(10000 * 10**16),
                decimals=18,
            ),
            type="BUY",
            asset_type="TOKEN",
            tries=[],
            created_at=0,
            status="SUCCESS",
            trigger="MANUAL",
        ),
    ]


@fixture
def transactions():
    return [
        Transaction(
            id="f9bd9283-fea4-4e2d-9f3c-4ad0b66503ef",
            sell_balance=BalanceAtomic(
                asset=usdt_token,
                amount=Decimal("100.00"),
                amount_atomic=int(10000 * 10**16),
                decimals=18,
            ),
            buy_balance=BalanceAtomic(
                asset=usdt_token,
                amount=Decimal("100.00"),
                amount_atomic=int(10000 * 10**16),
                decimals=18,
            ),
            executed_sell_balance=BalanceAtomic(
                asset=usdt_token,
                amount=Decimal("102.22"),
                amount_atomic=int(10222 * 10**16),
                decimals=18,
            ),
            executed_buy_balance=BalanceAtomic(
                asset=usdt_token,
                amount=Decimal("103.33"),
                amount_atomic=int(10333 * 10**16),
                decimals=18,
            ),
            type="BUY",
            created_at=0,
            transaction_hash="0x1234567890abcdef",
            order_id="f9bd9283-fea4-4e2d-9f3c-4ad0b66503ef",
            trigger="MANUAL",
            asset_type="TOKEN",
        )
    ]


@fixture
def postings():
    return [
        Posting(
            id="6dcba8f1-a95e-4d3f-b9c8-006c12082d0a",
            transaction_id="f9bd9283-fea4-4e2d-9f3c-4ad0b66503ef",
            asset_balance=BalanceAtomic(
                asset=usdt_token,
                amount=Decimal("1000"),
                amount_atomic=int(1000 * 10**18),
                decimals=18,
            ),
            created_at=0,
            type="BUY",
            asset_type="TOKEN",
        ),
        Posting(
            id="6dcba8f1-a95e-4d3f-b9c8-006c12082d0b-IN",
            transaction_id="f9bd9283-fea4-4e2d-9f3c-4ad0b66503ef",
            asset_balance=BalanceAtomic(
                asset=test_basket,
                amount=Decimal("50"),
                amount_atomic=int(50 * 10**18),
                decimals=18,
            ),
            created_at=0,
            type="BUY",
            asset_type="BASKET",
            basket_id="0d83917d-a2bd-4482-83e6-68d52c8f293a",
        ),
        Posting(
            id="6dcba8f1-a95e-4d3f-b9c8-006c12082d0c-IN",
            transaction_id="f9bd9283-fea4-4e2d-9f3c-4ad0b66503ef",
            asset_balance=BalanceAtomic(
                asset=eth_token,
                amount=Decimal("100"),
                amount_atomic=int(100 * 10**18),
                decimals=18,
            ),
            created_at=0,
            type="BUY",
            asset_type="TOKEN",
            basket_id="0d83917d-a2bd-4482-83e6-68d52c8f293a",
            parent_posting_id="6dcba8f1-a95e-4d3f-b9c8-006c12082d0b-IN",
        ),
        Posting(
            id="6dcba8f1-a95e-4d3f-b9c8-006c12082d0d-IN",
            transaction_id="f9bd9283-fea4-4e2d-9f3c-4ad0b66503ef",
            asset_balance=BalanceAtomic(
                asset=btc_token,
                amount=Decimal("60"),
                amount_atomic=int(60 * 10**18),
                decimals=18,
            ),
            created_at=0,
            type="BUY",
            asset_type="TOKEN",
            basket_id="0d83917d-a2bd-4482-83e6-68d52c8f293a",
            parent_posting_id="6dcba8f1-a95e-4d3f-b9c8-006c12082d0b-IN",
        ),
    ]


@fixture
def investment_plan_buy_only_tokens():
    return InvestmentPlan(
        steps=[
            InvestmentPlanStep(
                buy_balance=Balance(
                    amount=Decimal("1"),
                    asset=sol_token,
                ),
                sell_balance=Balance(
                    asset=usdt_token,
                    amount=Decimal("7"),
                ),
            ),
            InvestmentPlanStep(
                buy_balance=Balance(
                    asset=btc_token,
                    amount=Decimal("0.001"),
                ),
                sell_balance=Balance(
                    asset=usdt_token,
                    amount=Decimal(1),
                ),
            ),
        ]
    )


@fixture
def investment_plan_sell_only_basket():
    return InvestmentPlan(
        steps=[
            InvestmentPlanStep(
                buy_balance=Balance(
                    amount=Decimal("1"),
                    asset=sol_token,
                ),
                sell_balance=Balance(
                    asset=test_basket,
                    amount=Decimal("7"),
                ),
            ),
        ]
    )


async def fetch_all_orders(excluded_order_ids: list[str] = []):
    async with make_session() as session:
        result = await session.execute(
            select(OrderModel)
            .where(~OrderModel.id.in_(excluded_order_ids))
            .order_by(OrderModel.asset_type.asc())
        )
        rows = result.scalars().all()
        return rows


async def fetch_all_transactions(excluded_transaction_ids: list[str] = []):
    async with make_session() as session:
        result = await session.execute(
            select(TransactionModel)
            .where(~TransactionModel.id.in_(excluded_transaction_ids))
            .order_by(TransactionModel.created_at.asc())
        )
        rows = result.scalars().all()
        return rows


async def fetch_all_postings(excluded_posting_ids: list[str] = []):
    async with make_session() as session:
        result = await session.execute(
            select(PostingModel)
            .where(~PostingModel.id.in_(excluded_posting_ids))
            .order_by(PostingModel.created_at.asc())
        )
        rows = result.scalars().all()
        return rows


async def wait_for_orders():
    await sleep(45)


@mark.asyncio(loop_scope="session")
async def test_integration_execute_investment_plan_use_case_only_tokens(
    investment_plan_buy_only_tokens: InvestmentPlan,
    seed_fixtures: Any,  # noqa: F811
    cleanup_all: Any,  # noqa: F811
):
    await execute_investment_plan_use_case.execute(investment_plan_buy_only_tokens)

    await wait_for_orders()

    orders = list(await fetch_all_orders(["f9bd9283-fea4-4e2d-9f3c-4ad0b66503ef"]))

    assert len(orders) == 2

    # Token orders
    assert orders[0].status == "SUCCESS"
    assert orders[0].asset_type == "TOKEN"

    assert orders[1].status == "SUCCESS"
    assert orders[1].asset_type == "TOKEN"

    transactions = list(
        await fetch_all_transactions(["f9bd9283-fea4-4e2d-9f3c-4ad0b66503ef"])
    )

    assert len(transactions) == 2

    # Check if all transactions are linked to the correct orders regardless of order
    assert all(
        transaction.order_id in [order.id for order in orders]
        for transaction in transactions
    )

    postings = list(
        await fetch_all_postings(
            [
                "6dcba8f1-a95e-4d3f-b9c8-006c12082d0a",
                "6dcba8f1-a95e-4d3f-b9c8-006c12082d0b-IN",
                "6dcba8f1-a95e-4d3f-b9c8-006c12082d0c-IN",
                "6dcba8f1-a95e-4d3f-b9c8-006c12082d0d-IN",
            ]
        )
    )

    assert len(postings) == 4

    assert all(
        transaction.order_id in [order.id for order in orders]
        for transaction in transactions
    )

    # Check if all buy balances are reflected in postings
    assert all(
        [
            posting.id
            in [
                f"{transaction.id}-{suffix}"
                for transaction in transactions
                for suffix in ("IN", "OUT")
            ]
            for posting in postings
        ]
    )


@mark.asyncio(loop_scope="session")
async def test_integration_execute_investment_plan_use_case_only_basket(
    investment_plan_sell_only_basket: InvestmentPlan,
    seed_fixtures: Any,  # noqa: F811
    cleanup_all: Any,  # noqa: F811
):
    await execute_investment_plan_use_case.execute(investment_plan_sell_only_basket)

    await wait_for_orders()

    orders = list(await fetch_all_orders(["f9bd9283-fea4-4e2d-9f3c-4ad0b66503ef"]))

    assert len(orders) == 3

    # Basket order
    assert orders[0].status == "SUCCESS"
    assert orders[0].asset_type == "BASKET"

    # Token orders
    assert orders[1].status == "SUCCESS"
    assert orders[1].asset_type == "TOKEN"

    assert orders[2].status == "SUCCESS"
    assert orders[2].asset_type == "TOKEN"

    transactions = list(
        await fetch_all_transactions(["f9bd9283-fea4-4e2d-9f3c-4ad0b66503ef"])
    )

    assert len(transactions) == 3

    # Check if all transactions are linked to the correct orders regardless of order
    assert all(
        transaction.order_id in [order.id for order in orders]
        for transaction in transactions
    )

    postings = list(
        await fetch_all_postings(
            [
                "6dcba8f1-a95e-4d3f-b9c8-006c12082d0a",
                "6dcba8f1-a95e-4d3f-b9c8-006c12082d0b-IN",
                "6dcba8f1-a95e-4d3f-b9c8-006c12082d0c-IN",
                "6dcba8f1-a95e-4d3f-b9c8-006c12082d0d-IN",
            ]
        )
    )

    assert len(postings) == 5

    assert (
        len(
            [
                posting
                for posting in postings
                if posting.asset_id == test_basket.id and posting.amount_atomic < 0
            ]
        )
        == 1
    )

    assert (
        len(
            [
                posting
                for posting in postings
                if posting.asset_id == btc_token.id and posting.amount_atomic < 0
            ]
        )
        == 1
    )

    assert (
        len(
            [
                posting
                for posting in postings
                if posting.asset_id == eth_token.id and posting.amount_atomic < 0
            ]
        )
        == 1
    )
