import datetime
from jwt import decode
from typing import Any, cast
from environs import env
from web3 import AsyncWeb3
from siwe import SiweMessage, ISO8601Datetime
from eth_account.messages import encode_defunct
import requests


app_port = env.int("APP_PORT")
frontend_url = (
    env.str("FRONTEND_URL").split(",")[0].replace("https://", "").replace("http://", "")
)
credential = env.str("TEST_CREDENTIAL")

public_key = "0xb63b6f61569ebc3c08e7c235c355844da54d240e"
private_key = "0xe6bf9b3ab47ce317433bd33c21d00c6d066fce707a2c2dd31217c253620bcafc"


def test_integration_auth_verify_invalid_signature():
    nonce = "Y5WhT4JKiJr"

    w3 = AsyncWeb3()

    message = SiweMessage(
        domain=frontend_url,
        address=w3.to_checksum_address(public_key),
        statement="Sign in with Ethereum to the app.",
        uri="http://localhost",
        version=cast(Any, "1"),
        chain_id=1,
        nonce=nonce,
        issued_at=ISO8601Datetime(
            datetime.datetime.now().replace(microsecond=0).isoformat() + "Z"
        ),
    )

    response_1 = requests.post(
        f"http://localhost:{app_port}/auth/verify",
        cookies={"nonce": nonce},
        json={
            "signature": "0xinvalidsignature",
            "message": message.prepare_message(),
        },
        timeout=60,
    )

    assert response_1.status_code == 401


def test_integration_auth_verify_success():
    nonce = "Y5WhT4JKiJr"

    w3 = AsyncWeb3()

    message = SiweMessage(
        domain=frontend_url,
        address=w3.to_checksum_address(public_key),
        statement="Sign in with Ethereum to the app.",
        uri="http://localhost",
        version=cast(Any, "1"),
        chain_id=1,
        nonce=nonce,
        issued_at=ISO8601Datetime(
            datetime.datetime.now().replace(microsecond=0).isoformat() + "Z"
        ),
    )

    signable_message = encode_defunct(text=message.prepare_message())

    signed_message = w3.eth.account.sign_message(
        signable_message, private_key=private_key
    )

    response_1 = requests.post(
        f"http://localhost:{app_port}/auth/verify",
        cookies={"nonce": nonce},
        json={
            "signature": signed_message.signature.hex(),
            "message": message.prepare_message(),
        },
        timeout=60,
    )

    response_1_json = response_1.json()

    assert response_1.status_code == 200

    assert response_1.cookies.get("nonce") is None

    credential_payload = decode(
        response_1_json["credential"], options={"verify_signature": False}
    )

    assert credential_payload["address"].lower() == public_key.lower()
    assert isinstance(credential_payload["exp"], int)
