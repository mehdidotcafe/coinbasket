from environs import env
import requests


app_port = env.int("APP_PORT")


def test_integration_get_auth_nonce():
    response_1 = requests.get(
        f"http://localhost:{app_port}/auth/nonce",
        timeout=60,
    )

    response_1_json = response_1.json()

    assert response_1.status_code == 200

    assert response_1_json["nonce"] is not None
    assert isinstance(response_1_json["nonce"], str)

    cookie_nonce = response_1.headers["set-cookie"].split("nonce=")[1].split(";")[0]
    assert cookie_nonce == response_1_json["nonce"]
