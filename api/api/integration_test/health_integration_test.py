import requests
from environs import env

agent_port = env.int("AGENT_PORT")


def test_integration_health():
    response = requests.get(f"http://localhost:{agent_port}/health", timeout=5)

    assert response.status_code == 200
    assert response.json() == {"status": "OK"}
