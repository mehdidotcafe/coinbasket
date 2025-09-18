import requests
from environs import env

agent_port = env.int("AGENT_PORT")
agent_key = env.str("AGENT_KEY")


def test_integration_get_all_baskets(snapshot):
    response = requests.post(
      f"http://localhost:{agent_port}/basket",
      json={
          "agent_key": agent_key
      },
      timeout=5
    )

    assert response.status_code == 200
    assert response.json() == snapshot
