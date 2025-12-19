from unittest import mock
from api.authentication.credential.credential_generator import CredentialGenerator
from api.authentication.siwe.exception.invalid_signature import InvalidSignature
from api.authentication.siwe.siwe_manager import SiweManager
from api.authentication.verify_auth_use_case import VerifyAuthUseCase
from api.datetime.date_time import DateTime
from pytest import fixture, mark, raises


@fixture
def siwe_manager():
    return mock.Mock(spec=SiweManager)


@fixture
def credential_generator():
    return mock.Mock(spec=CredentialGenerator)


@fixture
def date_time():
    dt = mock.Mock(spec=DateTime)

    dt.now.return_value = 0
    return dt


@fixture
def use_case(
    siwe_manager: SiweManager,
    credential_generator: CredentialGenerator,
    date_time: DateTime,
):
    return VerifyAuthUseCase(
        siwe_manager=siwe_manager,
        credential_generator=credential_generator,
        date_time=date_time,
    )


@mark.asyncio
async def test_verify_auth_use_case_execute_invalid_signature(
    use_case: VerifyAuthUseCase,
    siwe_manager: SiweManager,
    credential_generator: CredentialGenerator,
):
    signature = "0xInvalidSignedMessage"
    message = "This is a test message."
    nonce = "random_nonce"
    domain = "example.com"

    siwe_manager.verify_signature.return_value = None

    with raises(InvalidSignature):
        await use_case.execute(signature, message, nonce, domain)

    credential_generator.generate_credential.assert_not_called()


@mark.asyncio
async def test_verify_auth_use_case_execute_success(
    use_case: VerifyAuthUseCase,
    siwe_manager: SiweManager,
    credential_generator: CredentialGenerator,
):
    signature = "0xsignedmessage"
    message = "This is a test message."
    claims: dict[str, str | int] = {
        "address": "0x1234567890abcdef1234567890abcdef12345678",
        "exp": 1716239022,
    }
    credential = "ey.jwt.token"
    nonce = "random_nonce"
    domain = "example.com"

    siwe_manager.verify_signature.return_value = claims
    credential_generator.generate_credential.return_value = credential

    res_credential, res_claims = await use_case.execute(
        signature, message, nonce, domain
    )

    assert res_credential == credential
    assert res_claims == {
        "address": claims["address"],
        "exp": 21600,
    }
