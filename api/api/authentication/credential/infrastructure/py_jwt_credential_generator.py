from jwt import encode
from api.authentication.credential.credential_generator import CredentialGenerator


class PyJwtCredentialGenerator(CredentialGenerator):
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def generate_credential(self, payload: dict[str, str | int]) -> str:
        token = encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
