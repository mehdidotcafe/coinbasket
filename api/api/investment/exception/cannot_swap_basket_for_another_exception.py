class CannotSwapBasketForAnotherException(Exception):
    """
    Exception raised when an attempt is made to swap one basket for another,
    which is not allowed.
    """

    def __init__(self, message="Cannot swap one basket for another."):
        super().__init__(message)
        self.message = message
