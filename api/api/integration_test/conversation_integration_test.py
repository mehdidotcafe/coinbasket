from dataclasses import asdict
from decimal import Decimal
import json
from typing import Any
from api.chain.balance import Balance, BalanceAtomic
from api.chain.chain import Gas
from api.conversation.message import QueryMessage
from api.investment.confirmed_order import ConfirmedOrder
from api.investment.exchange.exchange import SignableTransaction
from api.investment.planned_order import PlannedOrder, PlannedOrderBalance
from api.investment.signable_order import SignableOrder
from pytest import fixture
import requests
from environs import env
from api.test.database.cleanup_all import cleanup_all  # noqa: F401
from api.test.database.seed_fixtures import seed_fixtures  # noqa: F401
from api.protocol.fixture.token import btc_token, eth_token
from syrupy.filters import paths

app_port = env.int("APP_PORT")
credential = env.str("TEST_CREDENTIAL")


@fixture
def planned_orders():
    return [
        PlannedOrder(
            id="planned_order_1",
            address="0x1234567890abcdef1234567890abcdef12345678",
            sell_asset_with_amount=PlannedOrderBalance(
                asset=btc_token,
                amount=Decimal("0.5"),
                available_amount=Decimal("1.0"),
            ),
            buy_asset_with_amount=PlannedOrderBalance(
                asset=eth_token,
                amount=Decimal("1.0"),
                available_amount=Decimal("2.0"),
            ),
        ),
    ]


@fixture
def confirmed_orders():
    return [
        ConfirmedOrder(
            id="confirmed_order_1",
            planned_order_id="planned_order_1",
            address="0x1234567890abcdef1234567890abcdef12345678",
            buy_balance=Balance(
                asset=eth_token,
                amount=Decimal("1.0"),
            ),
            sell_balance=Balance(
                asset=btc_token,
                amount=Decimal("0.5"),
            ),
        ),
    ]


@fixture
def signable_orders():
    return [
        SignableOrder(
            id="signable_order_1",
            confirmed_order_id="confirmed_order_1",
            address="0x1234567890abcdef1234567890abcdef12345678",
            buy_balance=BalanceAtomic(
                asset=eth_token,
                amount=Decimal("1.0"),
                amount_atomic=1000000000000000000,
                decimals=18,
            ),
            sell_balance=BalanceAtomic(
                asset=btc_token,
                amount=Decimal("0.5"),
                amount_atomic=50000000,
                decimals=8,
            ),
            signature_payload=None,
            transaction=SignableTransaction(
                type="SIGN",
                amount=0,
                data="0xabcdef",
                gas=Gas(gas=21000, gas_price=1000000000),
                to_address="0xabcdef1234567890abcdef1234567890abcdef12",
            ),
        ),
    ]


@fixture
def signed_order_request() -> dict[str, Any]:
    return {
        "status": "CONFIRM",
        "signable_order_id": "signable_order_1",
        # Real transaction hash for testing purposes
        "transaction_hash": "0x97b5dde11ab8d41bfa45e904ee82efc5135ec75b9d56f2adaa5b28e485c5ff39",
    }


def test_integration_conversation_invalid_credential():
    response = requests.post(
        f"http://localhost:{app_port}/conversation",
        cookies={"credential": f"{credential}_invalid"},
        json={
            "message": asdict(
                QueryMessage(
                    id="42",
                    is_resuming=False,
                    role="user",
                    content="Please invest in bitcoin. Don't ask for fund allocation.",
                    created_at="2023-10-01",
                )
            ),
        },
        timeout=60,
    )

    assert response.status_code == 401


def test_integration_conversation_success(
    signed_order_request: dict[str, Any],
    cleanup_all: Any,  # noqa: F811
    snapshot,
):
    response_1 = requests.post(
        f"http://localhost:{app_port}/conversation",
        cookies={"credential": credential},
        json={
            "message": asdict(
                QueryMessage(
                    id="42",
                    is_resuming=False,
                    role="user",
                    content="Please invest in bitcoin. Don't ask for fund allocation.",
                    created_at="2023-10-01",
                )
            ),
        },
        timeout=60,
    )

    response_1_json = response_1.json()

    assert response_1.status_code == 200

    # The agent may either respond with an interrupting UI or with a content message asking for confirmation
    if not response_1_json["is_interrupting"]:
        assert response_1_json["ui"] is None
        assert response_1_json["content"] is not None

        response_2 = requests.post(
            f"http://localhost:{app_port}/conversation",
            cookies={"credential": credential},
            json={
                "message": asdict(
                    QueryMessage(
                        id="42",
                        is_resuming=False,
                        role="user",
                        content="Yes, please invest.",
                        created_at="2023-10-01",
                    )
                ),
            },
            timeout=60,
        )

        response_2_json = response_2.json()

        assert response_2.status_code == 200
        assert response_2_json["is_interrupting"] is True
        assert response_2_json["content"] is None

        assert response_2_json["ui"] == snapshot(
            name="ethereum",
            exclude=paths(
                "args.planned_order.id",
                "args.planned_order.sell_asset_with_amount.amount",
                "args.planned_order.sell_asset_with_amount.amount",
                "args.planned_order.sell_asset_with_amount.available_amount",
                "args.planned_order.buy_asset_with_amount.amount",
                "args.planned_order.buy_asset_with_amount.amount",
                "args.planned_order.buy_asset_with_amount.available_amount",
            ),
        )
    else:
        assert response_1_json["content"] is None
        assert response_1_json["ui"] == snapshot(
            name="ethereum",
            exclude=paths(
                "args.planned_order.id",
                "args.planned_order.sell_asset_with_amount.amount",
                "args.planned_order.sell_asset_with_amount.amount"
                "args.planned_order.sell_asset_with_amount.available_amount",
                "args.planned_order.buy_asset_with_amount.amount",
                "args.planned_order.buy_asset_with_amount.amount",
                "args.planned_order.buy_asset_with_amount.available_amount",
            ),
        )

    response_3 = requests.post(
        f"http://localhost:{app_port}/conversation",
        cookies={"credential": credential},
        json={
            "message": asdict(
                QueryMessage(
                    id="42",
                    is_resuming=True,
                    role="user",
                    content=json.dumps(signed_order_request),
                    created_at="2023-10-01",
                )
            ),
        },
        timeout=60,
    )

    response_3_json = response_3.json()

    assert response_3.status_code == 200
    assert response_3_json["is_interrupting"] is False
    assert response_3_json["ui"] is None
    assert response_3_json["content"] is not None
