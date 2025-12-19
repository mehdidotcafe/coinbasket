import requests

from environs import env

app_port = env.int("APP_PORT")


def test_integration_auth_signout():
    response_1 = requests.post(
        f"http://localhost:{app_port}/auth/signout",
        timeout=60,
    )

    set_cookie_headers = response_1.headers["Set-Cookie"].split(", ")

    assert any('nonce=""' in header for header in set_cookie_headers)
    assert any('credential=""' in header for header in set_cookie_headers)

    assert response_1.status_code == 204
