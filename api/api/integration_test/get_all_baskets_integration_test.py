from dataclasses import asdict
from api.conversation.message import QueryMessage
import requests
from environs import env

app_port = env.int("APP_PORT")
credential = env.str("TEST_CREDENTIAL")


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
