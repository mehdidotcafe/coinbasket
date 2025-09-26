from decimal import Decimal
from invest_agent.chain.balance import BalanceAtomic
from invest_agent.investment.order.infrastructure.sql_alchemy_order_repository import (
    OrderModel,
)
from invest_agent.investment.order.order import Order
from invest_agent.investment.transaction.infrastructure.sql_alchemy_transaction_repository import (
    TransactionModel,
)
from invest_agent.investment.transaction.transaction import Transaction
from invest_agent.portfolio.posting.infrastructure.sql_alchemy_posting_repository import (
    PostingModel,
)
from invest_agent.portfolio.posting.posting import Posting
from invest_agent.test.database.make_session import make_session
from pytest import fixture
from protocol.fixture.token import sol_token, eth_token, usdt_token, cake_token
import requests
from environs import env
from invest_agent.test.database.cleanup_all import cleanup_all  # noqa: F401


agent_port = env.int("AGENT_PORT")
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
        ),
    ]


@fixture(scope="function")
async def seed_fixtures(
    orders: list[Order], transactions: list[Transaction], postings: list[Posting]
):
    async with make_session() as session:
        async with session.begin():
            for order in orders:
                session.add(OrderModel.from_domain(order))
            for transaction in transactions:
                session.add(TransactionModel.from_domain(transaction))
            for posting in postings:
                session.add(PostingModel.from_domain(posting))

    yield postings


# TODO: Enhance this test once zero_x API is mocked in integration tests
def test_integration_get_portfolio(postings: list[Posting], seed_fixtures, cleanup_all):  # noqa: F811
    response = requests.post(
        f"http://localhost:{agent_port}/portfolio",
        json={"agent_key": agent_key, "token": usdt_token.to_dict()},
        timeout=60,
    )

    assert response.status_code == 200

    portfolio = response.json()

    # Available Balance
    assert portfolio["available_balance"]["native_balance"] == {
        "amount": "10000",
        "amount_atomic": "10000000000000000000000",
        "asset": {
            "id": "bsc:0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
            "name": "Binance Coin",
            "display_name": "Binance Coin",
            "ticker": "BNB",
            "address": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
        },
        "decimals": 18,
    }

    assert Decimal(portfolio["available_balance"]["converted_balance"]["amount"]) > 0
    assert (
        Decimal(portfolio["available_balance"]["converted_balance"]["amount_atomic"])
        > 0
    )
    assert portfolio["available_balance"]["converted_balance"]["asset"] == {
        "id": "bsc:0x55d398326f99059ff775485246999027b3197955",
        "name": "Tether USD",
        "display_name": "Tether USD",
        "ticker": "USDT",
        "address": "0x55d398326f99059ff775485246999027b3197955",
    }

    # Holding Balances
    assert portfolio["holding_balances"][0]["native_balance"] == {
        "amount": "9.99",
        "amount_atomic": "9990000000000000000",
        "asset": {
            "id": "bsc:0x55d398326f99059ff775485246999027b3197955",
            "name": "Tether USD",
            "display_name": "Tether USD",
            "ticker": "USDT",
            "address": "0x55d398326f99059ff775485246999027b3197955",
        },
        "decimals": 18,
    }

    for i in range(0, 2):
        assert (
            Decimal(portfolio["holding_balances"][i]["converted_balance"]["amount"]) > 0
        )
        assert (
            Decimal(
                portfolio["holding_balances"][i]["converted_balance"]["amount_atomic"]
            )
            > 0
        )
        assert portfolio["holding_balances"][i]["converted_balance"]["asset"] == {
            "id": "bsc:0x55d398326f99059ff775485246999027b3197955",
            "name": "Tether USD",
            "display_name": "Tether USD",
            "ticker": "USDT",
            "address": "0x55d398326f99059ff775485246999027b3197955",
        }

    # Total balance
    assert Decimal(portfolio["total_balance"]["amount"]) > 0
    assert Decimal(portfolio["total_balance"]["amount_atomic"]) > 0
    assert portfolio["total_balance"]["asset"] == {
        "id": "bsc:0x55d398326f99059ff775485246999027b3197955",
        "name": "Tether USD",
        "display_name": "Tether USD",
        "ticker": "USDT",
        "address": "0x55d398326f99059ff775485246999027b3197955",
    }

    # Pending Orders
    assert portfolio["pending_orders"] == [
        {
            "id": "cac0d510-d084-4881-967c-003c6d32983e",
            "sell_balance": {
                "amount": "100.00",
                "amount_atomic": "100000000000000000000",
                "asset": {
                    "id": "bsc:0x55d398326f99059ff775485246999027b3197955",
                    "name": "Tether USD",
                    "display_name": "Tether USD",
                    "ticker": "USDT",
                    "address": "0x55d398326f99059ff775485246999027b3197955",
                },
                "decimals": 18,
            },
            "buy_balance": {
                "amount": "100.00",
                "amount_atomic": "100000000000000000000",
                "asset": {
                    "id": "bsc:0x55d398326f99059ff775485246999027b3197955",
                    "name": "Tether USD",
                    "display_name": "Tether USD",
                    "ticker": "USDT",
                    "address": "0x55d398326f99059ff775485246999027b3197955",
                },
                "decimals": 18,
            },
            "type": "BUY",
            "tries": [],
            "created_at": 0,
            "status": "PENDING",
            "trigger": "MANUAL",
        }
    ]
