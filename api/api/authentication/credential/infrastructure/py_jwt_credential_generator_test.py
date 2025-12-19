from re import compile
from api.authentication.credential.infrastructure.py_jwt_credential_generator import (
    PyJwtCredentialGenerator,
)


JWT_RE = compile(r"^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$")


def test_generate_credential():
    generator = PyJwtCredentialGenerator(secret_key="my_secret")
    payload: dict[str, str | int] = {
        "address": "0x1234567890abcdef1234567890abcdef12345678",
        "exp": 1716239022,
    }
    token = generator.generate_credential(payload)

    assert isinstance(token, str)

    # Basic check to see if the token matches the JWT format
    assert JWT_RE.fullmatch(token) is not None
