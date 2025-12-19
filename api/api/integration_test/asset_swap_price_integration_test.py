import requests
from environs import env
from api.protocol.fixture.token import btc_token, eth_token
from api.protocol.fixture.basket import big4_basket, memecoinmania_basket
from syrupy.filters import paths

app_port = env.int("APP_PORT")
credential = env.str("TEST_CREDENTIAL")


def test_integration_asset_swap_price_sell_token_buy_token_invalid_credential():
    response = requests.post(
        f"http://localhost:{app_port}/asset/swap/price",
        cookies={"credential": f"{credential}_invalid"},
        json={
            "sell_asset": btc_token.to_dict(),
            "sell_asset_amount": "1",
            "buy_asset": eth_token.to_dict(),
        },
        timeout=60,
    )

    assert response.status_code == 401


def test_integration_asset_swap_price_sell_token_buy_token(snapshot):
    response = requests.post(
        f"http://localhost:{app_port}/asset/swap/price",
        cookies={"credential": credential},
        json={
            "sell_asset": btc_token.to_dict(),
            "sell_asset_amount": "1",
            "buy_asset": eth_token.to_dict(),
        },
        timeout=60,
    )

    response_json = response.json()

    assert response.status_code == 200
    assert response_json == snapshot(exclude=paths("buy_balance.amount"))


def test_integration_asset_swap_price_sell_token_buy_basket(snapshot):
    response = requests.post(
        f"http://localhost:{app_port}/asset/swap/price",
        cookies={"credential": credential},
        json={
            "sell_asset": btc_token.to_dict(),
            "sell_asset_amount": "1",
            "buy_asset": big4_basket.to_dict(),
        },
        timeout=60,
    )

    response_json = response.json()

    assert response.status_code == 200
    assert response_json == snapshot(exclude=paths("buy_balance.amount"))


def test_integration_asset_swap_price_sell_basket_buy_token(snapshot):
    response = requests.post(
        f"http://localhost:{app_port}/asset/swap/price",
        cookies={"credential": credential},
        json={
            "sell_asset": big4_basket.to_dict(),
            "sell_asset_amount": "1",
            "buy_asset": eth_token.to_dict(),
        },
        timeout=60,
    )

    response_json = response.json()

    assert response.status_code == 200
    assert response_json == snapshot(exclude=paths("buy_balance.amount"))


def test_integration_asset_swap_price_sell_basket_buy_basket():
    response = requests.post(
        f"http://localhost:{app_port}/asset/swap/price",
        cookies={"credential": credential},
        json={
            "sell_asset": big4_basket.to_dict(),
            "sell_asset_amount": "1",
            "buy_asset": memecoinmania_basket.to_dict(),
        },
        timeout=60,
    )

    assert response.status_code == 500
