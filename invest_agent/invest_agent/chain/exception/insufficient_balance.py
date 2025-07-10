from invest_agent.chain.balance import Balance


class InsufficientBalance(Exception):
    """Exception raised when there is insufficient balance for a transaction."""

    def __init__(self, min_balance: Balance):
        self.message = f"Insufficient balance. Minimum required: {min_balance.amount} {min_balance.token.ticker}. Please top up agent wallet."
        super().__init__(self.message)
