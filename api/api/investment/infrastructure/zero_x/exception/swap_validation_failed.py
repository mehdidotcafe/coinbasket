class SwapValidationFailed(Exception):
    def __init__(self, cause: Exception | None = None):
        self.message = "Swap validation failed."
        self.__cause__ = cause
        super().__init__(self.message)
