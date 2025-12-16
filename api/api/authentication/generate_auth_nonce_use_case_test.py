from unittest import mock
from api.authentication.generate_auth_nonce_use_case import GenerateAuthNonceUseCase
from api.authentication.siwe.siwe_manager import SiweManager
from pytest import fixture


@fixture
def siwe_manager():
    return mock.Mock(spec=SiweManager)


@fixture
def use_case(siwe_manager: SiweManager):
    return GenerateAuthNonceUseCase(siwe_manager=siwe_manager)


def test_generate_auth_nonce_use_case(
    siwe_manager: SiweManager, use_case: GenerateAuthNonceUseCase
):
    siwe_manager.generate_nonce.return_value = "unique_nonce_123"
    use_case = GenerateAuthNonceUseCase(siwe_manager)

    # Act
    nonce = use_case.execute()

    # Assert
    assert nonce == "unique_nonce_123"
