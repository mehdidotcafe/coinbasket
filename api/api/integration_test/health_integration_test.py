import requests
from environs import env

app_port = env.int("APP_PORT")


def test_integration_health():
    response = requests.get(f"http://localhost:{app_port}/health", timeout=5)

    assert response.status_code == 200
    assert response.json() == {"status": "OK"}
