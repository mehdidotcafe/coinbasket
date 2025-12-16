from abc import ABC, abstractmethod


class SiweManager(ABC):
    @abstractmethod
    def generate_nonce(self) -> str:
        raise NotImplementedError

    # @abstractmethod
    # def verify_message(self, message: str, signature: str) -> dict[str, Any] | None:
