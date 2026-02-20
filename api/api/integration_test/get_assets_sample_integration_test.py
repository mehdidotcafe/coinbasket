from dataclasses import asdict

from api.conversation.message import QueryMessage
from api.test.sse import concat_text_deltas, parse_sse_events
import requests
from environs import env

app_port = env.int("APP_PORT")
credential = env.str("TEST_CREDENTIAL")


def test_integration_get_assets_sample_invalid_credential():
    response = requests.post(
        f"http://localhost:{app_port}/conversation",
        cookies={"credential": f"{credential}_invalid"},
        json={
            "message": asdict(
                QueryMessage(
                    id="42",
                    is_resuming=False,
                    role="user",
                    content="What coins do you have? Show me a sample.",
                    created_at="2023-10-01",
                )
            ),
        },
        timeout=60,
    )

    assert response.status_code == 401


def test_integration_get_assets_sample():
    response_1 = requests.post(
        f"http://localhost:{app_port}/conversation",
        cookies={"credential": credential},
        json={
            "message": asdict(
                QueryMessage(
                    id="42",
                    is_resuming=False,
                    role="user",
                    content="What coins do you have? Show me a sample.",
                    created_at="2023-10-01",
                )
            ),
        },
        timeout=60,
    )

    assert response_1.status_code == 200

    events = parse_sse_events(response_1)

    concat_text = concat_text_deltas(events).lower()
    assert "0x7130d2a12b9bcbfae4f2634d864a1ee1ce3ead9c".lower() in concat_text
    assert "0x2170ed0880ac9a755fd29b2688956bd959f933f8".lower() in concat_text
    assert "0x55d398326f99059ff775485246999027b3197955".lower() in concat_text
    assert "0x1d2f0da169ceb9fc7b3144628db156f3f6c60dbe".lower() in concat_text
    assert "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c".lower() in concat_text
