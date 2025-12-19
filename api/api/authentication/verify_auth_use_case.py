from api.authentication.credential.credential_generator import CredentialGenerator
from api.authentication.siwe.exception.invalid_signature import InvalidSignature
from api.authentication.siwe.siwe_manager import SiweManager
from api.datetime.date_time import DateTime

SIX_HOURS_IN_SECONDS = 6 * 60 * 60


class VerifyAuthUseCase:
    def __init__(
        self,
        siwe_manager: SiweManager,
        credential_generator: CredentialGenerator,
        date_time: DateTime,
    ):
        self.siwe_manager = siwe_manager
        self.credential_generator = credential_generator
        self.date_time = date_time

    async def execute(
        self, signature: str, message: str, nonce: str, domain: str
    ) -> tuple[str, dict[str, str | int]]:
        claims = await self.siwe_manager.verify_signature(
            signature, message, nonce, domain
        )

        if claims is None:
            raise InvalidSignature()

        credential_claims: dict[str, str | int] = {
            "address": claims["address"],
            "exp": self.date_time.now() + SIX_HOURS_IN_SECONDS,
        }

        credential = self.credential_generator.generate_credential(credential_claims)
        return credential, credential_claims
