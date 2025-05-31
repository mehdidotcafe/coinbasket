class NoBasketInvestment(Exception):
    """
    Exception raised when there is no basket investment available.
    This can occur when the user tries to perform an operation that requires
    a basket investment, but none exists in the current context.
    """

    def __init__(self):
        self.message = "No basket investment."
        super().__init__(self.message)
