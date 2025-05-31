class BasketAlreadyInvested(Exception):
    """Exception raised when a basket has already been invested in and a new investment is attempted."""

    def __init__(self):
        self.message = (
            "You already have an invested basket. You cannot invest another basket."
        )
        super().__init__(self.message)
