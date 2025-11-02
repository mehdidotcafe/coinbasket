import requests
from environs import env

agent_port = env.int("AGENT_PORT")
agent_key = env.str("AGENT_KEY")


def test_integration_get_asset_by_id(snapshot):
    response = requests.post(
        f"http://localhost:{agent_port}/asset",
        json={
            "agent_key": agent_key,
            "asset_id": "bsc:0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
        },
        timeout=5,
    )

    assert response.status_code == 200
    assert response.json() == snapshot
