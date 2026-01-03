from pytest import mark
from api.protocol.fixture.token import (
    usdt_token,
)
import requests
from environs import env
from api.test.database.cleanup_all import cleanup_all  # noqa: F401
from api.test.database.seed_fixtures import seed_fixtures  # noqa: F401
from syrupy.filters import paths


app_port = env.int("APP_PORT")
credential = env.str("TEST_CREDENTIAL")


def test_integration_get_portfolio_invalid_credential():
    response = requests.post(
        f"http://localhost:{app_port}/portfolio",
        cookies={"credential": f"{credential}_invalid"},
        json={"token": usdt_token.to_dict()},
        timeout=60,
    )

    assert response.status_code == 401


# TODO: Enhance this test once zero_x API is mocked in integration tests
@mark.skip(reason="Portfolio management is currently disabled")
def test_integration_get_portfolio(seed_fixtures, cleanup_all, snapshot):  # noqa: F811
    response = requests.post(
        f"http://localhost:{app_port}/portfolio",
        cookies={"credential": credential},
        json={"token": usdt_token.to_dict()},
        timeout=60,
    )

    assert response.status_code == 200

    assert response.json() == snapshot(
        exclude=paths(
            "available_balance.converted_balance.amount",
            "available_balance.converted_balance.amount_atomic",
            "holding_balances.0.converted_balance.amount",
            "holding_balances.0.converted_balance.amount_atomic",
            "holding_balances.1.converted_balance.amount",
            "holding_balances.1.converted_balance.amount_atomic",
            "holding_balances.2.converted_balance.amount",
            "holding_balances.2.converted_balance.amount_atomic",
            "total_balance.amount",
            "total_balance.amount_atomic",
        )
    )
