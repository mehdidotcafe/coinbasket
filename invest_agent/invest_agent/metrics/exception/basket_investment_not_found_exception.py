class BasketInvestmentNotFoundException(Exception):
    """
    Exception raised when a basket is not found.
    """

    def __init__(self):
        self.message = "Basket investment not found."
        super().__init__(self.message)
