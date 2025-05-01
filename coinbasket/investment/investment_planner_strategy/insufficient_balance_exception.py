from coinbasket.chain.balance import Balance


class InsufficientBalanceException(Exception):
    """Exception raised when there is insufficient balance for a transaction."""

    def __init__(self, minBalance: Balance):
        self.message = f"Insufficient balance. Minimum required: {minBalance.amount} {minBalance.token.ticker}"
        super().__init__(self.message)
