from invest_agent.chain.balance import Balance


class InsufficientBalance(Exception):
    """Exception raised when there is insufficient balance for a transaction."""

    def __init__(self, minBalance: Balance):
        self.message = f"Insufficient balance. Minimum required: {minBalance.amount} {minBalance.token.ticker}. Please top up agent wallet."
        super().__init__(self.message)
