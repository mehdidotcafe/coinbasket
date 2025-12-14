from dataclasses import asdict
import json
from typing import Any
from api.conversation.message import QueryMessage
from pytest import fixture
import requests
from environs import env
from api.test.database.cleanup_all import cleanup_all  # noqa: F401
from syrupy.filters import paths

agent_port = env.int("AGENT_PORT")
agent_key = env.str("AGENT_KEY")


@fixture
def investment_plan() -> dict[str, Any]:
    return {
        "investment_plan": {
            "status": "CONFIRM",
            "steps": [
                {
                    "buy_balance": {
                        "asset": {
                            "id": "c0e724d3-c4d0-4bd0-973d-edd3907ecf51",
                            "description": "A basket of memecoins",
                            "name": "Memecoin Mania",
                            "display_name": "Memecoin Mania",
                            "ticker": "MEME",
                            "denomination": "0.1",
                            "tokens": [
                                {
                                    "id": "bsc:0xbA2aE424d960c26247Dd6c32edC70B295c744C43",
                                    "name": "Dogecoin",
                                    "display_name": "Dogecoin",
                                    "ticker": "DOGE",
                                    "address": "0xbA2aE424d960c26247Dd6c32edC70B295c744C43",
                                    "decimals": 8,
                                    "categories": ["meme", "dog"],
                                    "description": "A popular meme coin",
                                },
                                {
                                    "id": "bsc:0x2859e4544C4bB03966803b044A93563Bd2D0DD4D",
                                    "name": "Shiba Inu",
                                    "display_name": "Shiba Inu",
                                    "ticker": "SHIB",
                                    "address": "0x2859e4544C4bB03966803b044A93563Bd2D0DD4D",
                                    "decimals": 18,
                                    "categories": ["meme", "dog"],
                                    "description": "Another popular meme coin",
                                },
                            ],
                        },
                        "amount": "10.95",
                    },
                    "sell_balance": {
                        "asset": {
                            "id": "bsc:0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                            "name": "Binance Coin",
                            "display_name": "Binance Coin",
                            "ticker": "BNB",
                            "address": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                            "decimals": 18,
                            "categories": ["native"],
                            "description": "The native token of BNB Chain",
                        },
                        "amount": "15.95",
                    },
                }
            ],
        }
    }


def test_integration_conversation_buy_basket_and_token(
    investment_plan: dict[str, Any],
    cleanup_all: Any,  # noqa: F811
    snapshot,
):
    response_1 = requests.post(
        f"http://localhost:{agent_port}/conversation",
        json={
            "message": asdict(
                QueryMessage(
                    id="42",
                    is_resuming=False,
                    role="user",
                    content="Please invest in your memecoin mania basket and in bitcoin. Don't ask for fund allocation.",
                    created_at="2023-10-01",
                )
            ),
            "agent_key": agent_key,
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
            f"http://localhost:{agent_port}/conversation",
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
                "agent_key": agent_key,
            },
            timeout=60,
        )

        response_2_json = response_2.json()

        assert response_2.status_code == 200
        assert response_2_json["is_interrupting"] is True
        assert response_2_json["content"] is None

        assert response_2_json["ui"] == snapshot(
            exclude=paths(
                "args.priced_investment_plan.steps.0.sell_asset_with_amount.amount",
                "args.priced_investment_plan.steps.1.sell_asset_with_amount.amount",
                "args.priced_investment_plan.steps.0.buy_asset_with_amount.amount",
                "args.priced_investment_plan.steps.1.buy_asset_with_amount.amount",
            )
        )
    else:
        assert response_1_json["content"] is None
        assert response_1_json["ui"] == snapshot(
            exclude=paths(
                "args.priced_investment_plan.steps.0.sell_asset_with_amount.amount",
                "args.priced_investment_plan.steps.1.sell_asset_with_amount.amount",
                "args.priced_investment_plan.steps.0.buy_asset_with_amount.amount",
                "args.priced_investment_plan.steps.1.buy_asset_with_amount.amount",
            )
        )

    response_3 = requests.post(
        f"http://localhost:{agent_port}/conversation",
        json={
            "message": asdict(
                QueryMessage(
                    id="42",
                    is_resuming=True,
                    role="user",
                    content=json.dumps(investment_plan),
                    created_at="2023-10-01",
                )
            ),
            "agent_key": agent_key,
        },
        timeout=60,
    )

    response_3_json = response_3.json()

    assert response_3.status_code == 200
    assert response_3_json["is_interrupting"] is False
    assert response_3_json["ui"] is None
    assert response_3_json["content"] is not None
