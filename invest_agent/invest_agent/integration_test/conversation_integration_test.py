from dataclasses import asdict
import json
from typing import Any
from invest_agent.conversation.message import QueryMessage
from pytest import fixture
import requests
from environs import env

agent_port = env.int("AGENT_PORT")
agent_key = env.str("AGENT_KEY")


@fixture
def investment_plan() -> dict[str, Any]:
    return {
        "investment_plan": {
            "steps": [
                {
                    "buy_balance": {
                        "basket": {
                            "id": "c0e724d3-c4d0-4bd0-973d-edd3907ecf51",
                            "description": "A basket of memecoins",
                            "name": "Memecoin Mania",
                            "denomination": "0.1",
                            "balances": [
                                {
                                    "sell_balance": {
                                        "token": {
                                            "id": "bsc:0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                                            "name": "Binance Coin",
                                            "display_name": "Binance Coin",
                                            "ticker": "BNB",
                                            "address": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                                        },
                                        "amount": "10.95",
                                    },
                                    "buy_balance": {
                                        "token": {
                                            "id": "bsc:0xbA2aE424d960c26247Dd6c32edC70B295c744C43",
                                            "name": "Dogecoin",
                                            "display_name": "Dogecoin",
                                            "ticker": "DOGE",
                                            "address": "0xbA2aE424d960c26247Dd6c32edC70B295c744C43",
                                        },
                                        "amount": "1028983",
                                    },
                                },
                                {
                                    "sell_balance": {
                                        "token": {
                                            "id": "bsc:0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                                            "name": "Binance Coin",
                                            "display_name": "Binance Coin",
                                            "ticker": "BNB",
                                            "address": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                                        },
                                        "amount": "5.00",
                                    },
                                    "buy_balance": {
                                        "token": {
                                            "id": "bsc:0x2859e4544C4bB03966803b044A93563Bd2D0DD4D",
                                            "name": "Shiba Inu",
                                            "display_name": "Shiba Inu",
                                            "ticker": "SHIB",
                                            "address": "0x2859e4544C4bB03966803b044A93563Bd2D0DD4D",
                                        },
                                        "amount": "1028983",
                                    },
                                },
                            ],
                        },
                        "amount": "10.95",
                    },
                    "sell_balance": {
                        "token": {
                            "id": "bsc:0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                            "name": "Binance Coin",
                            "display_name": "Binance Coin",
                            "ticker": "BNB",
                            "address": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                        },
                        "amount": "15.95",
                    },
                }
            ]
        }
    }


def test_integration_conversation(
    investment_plan: dict[str, Any], cleanup_all: Any, snapshot: Any
):
    response_1 = requests.post(
        f"http://localhost:{agent_port}/conversation",
        json={
            "message": asdict(
                QueryMessage(
                    id="42",
                    is_resuming=False,
                    role="user",
                    content="Please invest in your memecoin mania basket and in bitcoin.",
                    created_at="2023-10-01",
                )
            ),
            "agent_key": agent_key,
        },
        timeout=60,
    )

    response_1_json = response_1.json()

    assert response_1.status_code == 200
    assert response_1_json["is_interrupting"] is False
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
    assert len(response_2_json["ui"]["args"]["intent_investment_plan"]["steps"]) == 2

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
