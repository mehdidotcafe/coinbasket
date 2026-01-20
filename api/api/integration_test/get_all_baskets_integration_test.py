from dataclasses import asdict
from api.conversation.message import QueryMessage
import requests
from environs import env

app_port = env.int("APP_PORT")
credential = env.str("TEST_CREDENTIAL")


def test_integration_get_all_baskets_invalid_credential():
    response = requests.post(
        f"http://localhost:{app_port}/conversation",
        cookies={"credential": f"{credential}_invalid"},
        json={
            "message": asdict(
                QueryMessage(
                    id="42",
                    is_resuming=False,
                    role="user",
                    content="What are your available baskets?",
                    created_at="2023-10-01",
                )
            ),
        },
        timeout=60,
    )

    assert response.status_code == 401


def test_integration_get_all_baskets():
    response_1 = requests.post(
        f"http://localhost:{app_port}/conversation",
        cookies={"credential": credential},
        json={
            "message": asdict(
                QueryMessage(
                    id="42",
                    is_resuming=False,
                    role="user",
                    content="What are your available baskets?",
                    created_at="2023-10-01",
                )
            ),
        },
        timeout=60,
    )

    response_1_json = response_1.json()

    assert response_1.status_code == 200
    assert response_1_json["is_interrupting"] is False
    assert response_1_json["ui"] is None
    assert (
        "0x2f8a339b5889ffac4c5a956787cda593b3c36867".lower()
        in response_1_json["content"].lower()
    )
