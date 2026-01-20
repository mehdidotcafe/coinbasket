from abc import ABC, abstractmethod

from api.authentication.credential.credential import Credential

Claims = dict[str, str | int]


class CredentialGenerator(ABC):
    @abstractmethod
    def generate_credential(self, payload: Claims) -> Credential:
        raise NotImplementedError

    @abstractmethod
    def verify_credential(self, credential: Credential) -> Claims | None:
        raise NotImplementedError
