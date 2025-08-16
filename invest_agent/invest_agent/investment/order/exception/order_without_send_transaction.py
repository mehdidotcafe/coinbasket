class OrderWithoutSendTransaction(Exception):
    """Exception raised when an order is waiting an has no SEND transaction (only SIGN)."""

    def __init__(self):
        self.message = "Order without SEND transaction."
        super().__init__(self.message)
