from abc import ABC, abstractmethod

from api.authentication.credential.credential import Credential


class CredentialGenerator(ABC):
    @abstractmethod
    def generate_credential(self, payload: dict[str, str | int]) -> Credential:
        raise NotImplementedError
