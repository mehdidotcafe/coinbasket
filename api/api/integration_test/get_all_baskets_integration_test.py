from dataclasses import asdict
from api.conversation.message import QueryMessage
import requests
from environs import env

agent_port = env.int("AGENT_PORT")
agent_key = env.str("AGENT_KEY")


def test_integration_get_all_baskets(
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
                    content="What are your available baskets?",
                    created_at="2023-10-01",
                )
            ),
            "agent_key": agent_key,
        },
        timeout=60,
    )

    response_json = response_1.json()

    print(f"Response json: {response_json}")

    assert response_1.status_code == 200
