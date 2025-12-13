from abc import ABC, abstractmethod

from protocol.token import Token


class TokenRepository(ABC):
    @abstractmethod
    async def get_by_address(self, address: str) -> Token | None:
        raise NotImplementedError
