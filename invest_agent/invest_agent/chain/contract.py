from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any


class Contract(ABC):
    @abstractmethod
    async def get_decimals(self, token_address: str) -> Decimal:
        """Get the number of decimals for the given token address."""
        raise NotImplementedError

    @abstractmethod
    def make_approve_transaction_input(
        self,
        token_address: str,
        spender_address: str,
        amount: Decimal,
    ) -> Any:
        """Generate an approve transaction for the given token."""
        raise NotImplementedError
