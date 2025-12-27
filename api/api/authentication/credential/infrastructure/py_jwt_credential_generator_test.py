from re import compile
from api.authentication.credential.infrastructure.py_jwt_credential_generator import (
    PyJwtCredentialGenerator,
)


JWT_RE = compile(r"^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$")


def test_generate_credential():
    generator = PyJwtCredentialGenerator(secret_key="my_secret")
    payload: dict[str, str | int] = {
        "address": "0x1234567890abcdef1234567890abcdef12345678",
        "exp": 3343991358,
    }
    token = generator.generate_credential(payload)

    assert isinstance(token, str)

    # Basic check to see if the token matches the JWT format
    assert JWT_RE.fullmatch(token) is not None


def test_verify_credential_valid_credential():
    generator = PyJwtCredentialGenerator(secret_key="my_secret")

    credential = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhZGRyZXNzIjoiMHgxMjM0NTY3ODkwYWJjZGVmMTIzNDU2Nzg5MGFiY2RlZjEyMzQ1Njc4IiwiZXhwIjozMzQzOTkxMzU4fQ.aAg93hP_AQ5-bbG9cReyYKn0ub2WmNtAkLcwpnePMCU"

    claims = generator.verify_credential(credential)

    assert claims == {
        "address": "0x1234567890abcdef1234567890abcdef12345678",
        "exp": 3343991358,
    }


def test_verify_credential_expired_credential():
    generator = PyJwtCredentialGenerator(secret_key="my_secret")

    credential = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhZGRyZXNzIjoiMHgxMjM0NTY3ODkwYWJjZGVmMTIzNDU2Nzg5MGFiY2RlZjEyMzQ1Njc4IiwiZXhwIjowfQ.W8_oiO2MSGTERT6BazJmx0pkmivjNXPoM-qiqCJKhQ"

    claims = generator.verify_credential(credential)

    assert claims is None


def test_verify_credential_invalid_signature():
    generator = PyJwtCredentialGenerator(secret_key="my_secret")
    credential = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhZGRyZXNzIjoiMHgxMjM0NTY3ODkwYWJjZGVmMTIzNDU2Nzg5MGFiY2RlZjEyMzQ1Njc4IiwiZXhwIjowfQ.INVALID_SIGNATURE"

    claims = generator.verify_credential(credential)

    assert claims is None
