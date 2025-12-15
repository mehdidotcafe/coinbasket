import requests
from environs import env
from protocol.fixture.token import btc_token, eth_token
from protocol.fixture.basket import big4_basket, memecoinmania_basket
from syrupy.filters import paths

app_port = env.int("APP_PORT")
agent_key = env.str("AGENT_KEY")


def test_integration_asset_swap_price_sell_token_buy_token(snapshot):
    response = requests.post(
        f"http://localhost:{app_port}/asset/swap/price",
        json={
            "sell_asset": btc_token.to_dict(),
            "sell_asset_amount": "1",
            "buy_asset": eth_token.to_dict(),
            "agent_key": agent_key,
        },
        timeout=60,
    )

    response_json = response.json()

    assert response.status_code == 200
    assert response_json == snapshot(exclude=paths("buy_balance.amount"))


def test_integration_asset_swap_price_sell_token_buy_basket(snapshot):
    response = requests.post(
        f"http://localhost:{app_port}/asset/swap/price",
        json={
            "sell_asset": btc_token.to_dict(),
            "sell_asset_amount": "1",
            "buy_asset": big4_basket.to_dict(),
            "agent_key": agent_key,
        },
        timeout=60,
    )

    response_json = response.json()

    assert response.status_code == 200
    assert response_json == snapshot(exclude=paths("buy_balance.amount"))


def test_integration_asset_swap_price_sell_basket_buy_token(snapshot):
    response = requests.post(
        f"http://localhost:{app_port}/asset/swap/price",
        json={
            "sell_asset": big4_basket.to_dict(),
            "sell_asset_amount": "1",
            "buy_asset": eth_token.to_dict(),
            "agent_key": agent_key,
        },
        timeout=60,
    )

    response_json = response.json()

    assert response.status_code == 200
    assert response_json == snapshot(exclude=paths("buy_balance.amount"))


def test_integration_asset_swap_price_sell_basket_buy_basket():
    response = requests.post(
        f"http://localhost:{app_port}/asset/swap/price",
        json={
            "sell_asset": big4_basket.to_dict(),
            "sell_asset_amount": "1",
            "buy_asset": memecoinmania_basket.to_dict(),
            "agent_key": agent_key,
        },
        timeout=60,
    )

    assert response.status_code == 500
