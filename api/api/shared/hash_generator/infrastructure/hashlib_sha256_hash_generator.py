import hashlib

from api.shared.hash_generator.hash_generator import HashGenerator


class HashlibSha256HashGenerator(HashGenerator):
    def generate(self, value: str) -> str:
        return hashlib.sha256(value.encode()).hexdigest()
