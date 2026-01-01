import requests
from environs import env
from api.protocol.fixture.token import btc_token, eth_token

app_port = env.int("APP_PORT")
credential = env.str("TEST_CREDENTIAL")


def test_integration_order_signable_invalid_credential():
    response = requests.post(
        f"http://localhost:{app_port}/order/signable",
        cookies={"credential": f"{credential}_invalid"},
        json={
            "buy_balance": {
                "asset": eth_token.to_dict(),
                "amount": "1.0",
            },
            "sell_balance": {
                "asset": btc_token.to_dict(),
                "amount": "0.5",
            },
        },
        timeout=60,
    )

    assert response.status_code == 401


def test_integration_order_signable_success(snapshot):
    response = requests.post(
        f"http://localhost:{app_port}/order/signable",
        cookies={"credential": credential},
        json={
            "buy_balance": {
                "asset": eth_token.to_dict(),
                "amount": "1.0",
            },
            "sell_balance": {
                "asset": btc_token.to_dict(),
                "amount": "0.5",
            },
        },
        timeout=60,
    )

    response_json = response.json()

    assert response.status_code == 200
    assert "buy_balance" in response_json
    assert "sell_balance" in response_json
    assert "transaction" in response_json
    assert response_json == snapshot
