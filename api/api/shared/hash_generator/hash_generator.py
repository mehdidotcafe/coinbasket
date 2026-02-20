from abc import ABC


class HashGenerator(ABC):
    def generate(self, value: str) -> str:
        raise NotImplementedError
