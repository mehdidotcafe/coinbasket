from api.chain.balance import BalanceAtomic
from api.protocol.token import Token


class InsufficientBalance(Exception):
    """Exception raised when there is insufficient balance for a transaction."""

    def __init__(self, min_balance: BalanceAtomic[Token]):
        self.message = f"Insufficient balance. Minimum required: {min_balance.amount} {min_balance.asset.ticker}. Please top up agent wallet."
        super().__init__(self.message)
