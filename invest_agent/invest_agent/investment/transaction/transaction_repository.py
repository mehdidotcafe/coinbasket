from abc import ABC, abstractmethod

from invest_agent.investment.transaction.transaction import Transaction


class TransactionRepository(ABC):
    @abstractmethod
    async def create_transaction(self, transaction: Transaction) -> Transaction:
        """Create a transaction to the repository."""
        raise NotImplementedError
