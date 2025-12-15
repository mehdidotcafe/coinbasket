from decimal import Decimal
from api.chain.balance import BalanceAtomic
from api.investment.order.order import Order
from api.investment.transaction.transaction import Transaction
from api.portfolio.posting.posting import Posting
from pytest import fixture
from protocol.fixture.token import (
    sol_token,
    eth_token,
    usdt_token,
    cake_token,
    shib_token,
)
import requests
from environs import env
from api.test.database.cleanup_all import cleanup_all  # noqa: F401
from api.test.database.seed_fixtures import seed_fixtures  # noqa: F401
from syrupy.filters import paths


app_port = env.int("APP_PORT")
agent_key = env.str("AGENT_KEY")


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
        Order(
            id="cac0d510-d084-4881-967c-003c6d32983e",
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
            status="PENDING",
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
                asset=sol_token,
                amount=Decimal("3.54"),
                amount_atomic=int(354 * 10**16),
                decimals=18,
            ),
            created_at=0,
            type="BUY",
            asset_type="TOKEN",
        ),
        Posting(
            id="6dcba8f1-a95e-4d3f-b9c8-006c12082d0b",
            transaction_id="f9bd9283-fea4-4e2d-9f3c-4ad0b66503ef",
            asset_balance=BalanceAtomic(
                asset=sol_token,
                amount=Decimal("-1.22"),
                amount_atomic=int(-122 * 10**16),
                decimals=18,
            ),
            created_at=0,
            type="SELL",
            asset_type="TOKEN",
        ),
        Posting(
            id="6dcba8f1-a95e-4d3f-b9c8-006c12082d0c",
            transaction_id="f9bd9283-fea4-4e2d-9f3c-4ad0b66503ef",
            asset_balance=BalanceAtomic(
                asset=eth_token,
                amount=Decimal("4.00"),
                amount_atomic=int(400 * 10**16),
                decimals=18,
            ),
            created_at=0,
            type="BUY",
            asset_type="TOKEN",
        ),
        Posting(
            id="6dcba8f1-a95e-4d3f-b9c8-006c12082d0d",
            transaction_id="f9bd9283-fea4-4e2d-9f3c-4ad0b66503ef",
            asset_balance=BalanceAtomic(
                asset=eth_token,
                amount=Decimal("6.83"),
                amount_atomic=int(683 * 10**16),
                decimals=18,
            ),
            created_at=0,
            type="SELL",
            asset_type="TOKEN",
        ),
        Posting(
            id="6dcba8f1-a95e-4d3f-b9c8-006c12082d0e",
            transaction_id="f9bd9283-fea4-4e2d-9f3c-4ad0b66503ef",
            asset_balance=BalanceAtomic(
                asset=usdt_token,
                amount=Decimal("9.99"),
                amount_atomic=int(999 * 10**16),
                decimals=18,
            ),
            created_at=0,
            type="BUY",
            asset_type="TOKEN",
        ),
        Posting(
            id="6dcba8f1-a95e-4d3f-b9c8-006c12082d1a",
            transaction_id="f9bd9283-fea4-4e2d-9f3c-4ad0b66503ef",
            asset_balance=BalanceAtomic(
                asset=cake_token,
                amount=Decimal("22.77"),
                amount_atomic=int(2277 * 10**16),
                decimals=18,
            ),
            created_at=0,
            type="BUY",
            asset_type="TOKEN",
        ),
        Posting(
            id="6dcba8f1-a95e-4d3f-b9c8-006c12082d1b",
            transaction_id="f9bd9283-fea4-4e2d-9f3c-4ad0b66503ef",
            asset_balance=BalanceAtomic(
                asset=cake_token,
                amount=Decimal("-22.77"),
                amount_atomic=int(-2277 * 10**16),
                decimals=18,
            ),
            created_at=0,
            type="SELL",
            asset_type="TOKEN",
        ),
        Posting(
            id="6dcba8f1-a95e-4d3f-b9c8-006c12082d1c",
            transaction_id="f9bd9283-fea4-4e2d-9f3c-4ad0b66503ef",
            asset_balance=BalanceAtomic(
                asset=shib_token,
                amount=Decimal("1"),
                amount_atomic=int(1 * 10**18),
                decimals=18,
            ),
            created_at=0,
            type="BUY",
            asset_type="TOKEN",
        ),
    ]


# TODO: Enhance this test once zero_x API is mocked in integration tests
def test_integration_get_portfolio(seed_fixtures, cleanup_all, snapshot):  # noqa: F811
    response = requests.post(
        f"http://localhost:{app_port}/portfolio",
        json={"agent_key": agent_key, "token": usdt_token.to_dict()},
        timeout=60,
    )

    assert response.status_code == 200

    assert response.json() == snapshot(
        exclude=paths(
            "available_balance.converted_balance.amount",
            "available_balance.converted_balance.amount_atomic",
            "holding_balances.0.converted_balance.amount",
            "holding_balances.0.converted_balance.amount_atomic",
            "holding_balances.1.converted_balance.amount",
            "holding_balances.1.converted_balance.amount_atomic",
            "holding_balances.2.converted_balance.amount",
            "holding_balances.2.converted_balance.amount_atomic",
            "total_balance.amount",
            "total_balance.amount_atomic",
        )
    )
