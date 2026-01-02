from abc import ABC, abstractmethod
from api.investment.signable_order import SignableOrder
from api.database.session import NullableSession


class SignableOrderRepository(ABC):
    @abstractmethod
    async def save(
        self, signable_order: SignableOrder, session: NullableSession = None
    ) -> SignableOrder:
        """Save a signable order to the repository."""
        raise NotImplementedError
