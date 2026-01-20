from abc import ABC, abstractmethod


class SiweManager(ABC):
    @abstractmethod
    def generate_nonce(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def verify_signature(
        self, signature: str, message: str, nonce: str, domain: str
    ) -> dict[str, str | int] | None:
        raise NotImplementedError
