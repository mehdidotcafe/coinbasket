from abc import ABC, abstractmethod
from invest_agent.investment.transaction.transaction import Transaction
from invest_agent.database.session import NullableSession


class TransactionRepository(ABC):
    @abstractmethod
    async def create_transaction(
        self, transaction: Transaction, session: NullableSession = None
    ) -> Transaction:
        """Create a transaction to the repository."""
        raise NotImplementedError

    @abstractmethod
    async def get_transactions(
        self, transaction_ids: list[str], session: NullableSession = None
    ) -> list[Transaction]:
        """Get transactions by their IDs."""
        raise NotImplementedError
