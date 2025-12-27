from api.authentication.credential.credential import Credential
from jwt import encode, decode
from api.authentication.credential.credential_generator import (
    CredentialGenerator,
    Claims,
)


class PyJwtCredentialGenerator(CredentialGenerator):
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def generate_credential(self, payload: Claims) -> str:
        token = encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def verify_credential(self, credential: Credential) -> Claims | None:
        try:
            decoded_payload = decode(
                credential,
                self.secret_key,
                algorithms=[self.algorithm],
                verify_exp=True,
            )
            return decoded_payload
        except Exception:
            return None
