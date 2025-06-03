class BasketAlreadyInvested(Exception):
    """Exception raised when a basket has already been invested in and a new investment is attempted."""

    def __init__(self):
        self.message = "You already have an invested basket. Please divest the basket before investing in a new one."
        super().__init__(self.message)
