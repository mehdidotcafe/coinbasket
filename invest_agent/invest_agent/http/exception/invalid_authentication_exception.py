class InvalidAuthenticationException(Exception):
    """Exception raised for invalid Agent key errors."""

    def __init__(self):
        self.message = "Invalid Authentication."
        super().__init__(self.message)
