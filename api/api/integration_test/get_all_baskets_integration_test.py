from dataclasses import asdict

from api.conversation.message import QueryMessage
from api.test.sse import concat_text_deltas, parse_sse_events
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

    assert response_1.status_code == 200

    events = parse_sse_events(response_1)

    concat_text = concat_text_deltas(events)
    assert "0x2f8a339b5889ffac4c5a956787cda593b3c36867".lower() in concat_text.lower()
