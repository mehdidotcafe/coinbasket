from dataclasses import asdict
import json
from typing import Any
from api.conversation.message import QueryMessage
from pytest import fixture
import requests
from environs import env
from api.test.database.cleanup_all import cleanup_all  # noqa: F401
from syrupy.filters import paths

app_port = env.int("APP_PORT")
credential = env.str("TEST_CREDENTIAL")


@fixture
def signed_order_request() -> dict[str, Any]:
    return {
        "status": "CONFIRM",
        "transaction_hash": "0x123456789abcdef",
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


def test_integration_conversation(
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
