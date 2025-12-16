from api.authentication.siwe.siwe_manager import SiweManager


class GenerateAuthNonceUseCase:
    def __init__(self, siwe_manager: SiweManager):
        self.siwe_manager = siwe_manager

    def execute(self) -> str:
        return self.siwe_manager.generate_nonce()
