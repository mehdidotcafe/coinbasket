import hashlib
import uuid


class IdGenerator:
    """
    A class to generate unique IDs for data ingestion.
    """

    def __init__(self):
        self.current_id = 0

    def generate_id(self, seed: str) -> str:
        """
        Generates a unique ID (UUID) based on seed.
        """
        hash_bytes = hashlib.sha256(seed.encode()).digest()

        return str(uuid.UUID(bytes=hash_bytes[:16]))
