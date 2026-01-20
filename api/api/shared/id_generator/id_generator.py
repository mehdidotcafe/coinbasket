import hashlib
import uuid


class IdGenerator:
    """
    A class to generate unique IDs for data ingestion.
    """

    def generate_id(self, seed: str) -> str:
        """
        Generates a unique ID (UUID) based on seed.
        """
        hash_bytes = hashlib.sha256(seed.encode()).digest()

        return str(uuid.UUID(bytes=hash_bytes[:16]))

    def generate_random_id(self) -> str:
        """
        Generates a random UUID.
        """
        return str(uuid.uuid4())
