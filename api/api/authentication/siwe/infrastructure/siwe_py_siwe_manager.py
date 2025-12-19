from api.authentication.siwe.siwe_manager import SiweManager
from siwe import generate_nonce, SiweMessage


class SiwePySiweManager(SiweManager):
    def generate_nonce(self) -> str:
        return generate_nonce()

    async def verify_signature(
        self, signature: str, message: str, nonce: str, domain: str
    ) -> dict[str, str | int] | None:
        siwe_message = SiweMessage.from_message(message=message)
        try:
            siwe_message.verify(signature, nonce=nonce, domain=domain)
        except Exception as e:
            print(f"SIWE verification failed: {e}")
            return None

        return siwe_message.model_dump()
