from decimal import Decimal
from api.investment.confirmed_order import ConfirmedOrder
from api.investment.fees import Fees
from api.investment.planned_order import PlannedOrder, PlannedOrderBalance
from api.investment.signable_order import SignableOrder
from pytest import fixture
import requests
from environs import env
from api.protocol.fixture.token import btc_token, eth_token
from syrupy.filters import paths
from api.chain.balance import BalanceAtomic

from api.test.database.cleanup_all import cleanup_all  # noqa: F401
from api.test.database.seed_fixtures import seed_fixtures  # noqa: F401


app_port = env.int("APP_PORT")
credential = env.str("TEST_CREDENTIAL")


@fixture
def planned_orders():
    return [
        PlannedOrder(
            id="planned_order_1",
            address="0x1234567890abcdef1234567890abcdef12345678",
            sell_asset_with_amount=PlannedOrderBalance(
                asset=btc_token,
                amount=Decimal("0.5"),
                available_amount=Decimal("1.0"),
            ),
            buy_asset_with_amount=PlannedOrderBalance(
                asset=eth_token,
                amount=Decimal("1.0"),
                available_amount=Decimal("2.0"),
            ),
            fees=Fees(
                gas_fee=BalanceAtomic(
                    asset=eth_token,
                    amount=Decimal("0.03"),
                    amount_atomic=30000000000000000,
                    decimals=18,
                ),
                provider_fee=BalanceAtomic(
                    asset=eth_token,
                    amount=Decimal("0.08"),
                    amount_atomic=80000000000000000,
                    decimals=18,
                ),
                platform_fee=BalanceAtomic(
                    asset=eth_token,
                    amount=Decimal("0.01"),
                    amount_atomic=10000000000000000,
                    decimals=18,
                ),
            ),
        ),
    ]


@fixture
def confirmed_orders() -> list[ConfirmedOrder]:
    return []


@fixture
def signable_orders() -> list[SignableOrder]:
    return []


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


def test_integration_order_signable_success(seed_fixtures, cleanup_all, snapshot):  # noqa: F811
    response = requests.post(
        f"http://localhost:{app_port}/order/signable",
        cookies={"credential": credential},
        json={
            "planned_order_id": "planned_order_1",
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

    assert response_json == snapshot(exclude=paths("id"))
