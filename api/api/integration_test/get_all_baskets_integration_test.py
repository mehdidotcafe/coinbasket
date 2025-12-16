from dataclasses import asdict
from api.conversation.message import QueryMessage
import requests
from environs import env

app_port = env.int("APP_PORT")
app_key = env.str("APP_KEY")


def test_integration_get_all_baskets(
    snapshot,
):
    response_1 = requests.post(
        f"http://localhost:{app_port}/conversation",
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
            "app_key": app_key,
        },
        timeout=60,
    )

    response_json = response_1.json()

    print(f"Response json: {response_json}")

    assert response_1.status_code == 200
