from api.authentication.siwe.siwe_manager import SiweManager
from siwe import generate_nonce


class SiwePySiweManager(SiweManager):
    def generate_nonce(self) -> str:
        return generate_nonce()
