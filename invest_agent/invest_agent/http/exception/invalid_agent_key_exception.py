class InvalidAgentKeyException(Exception):
    """Exception raised for invalid Agent key errors."""

    def __init__(self):
        self.message = "Invalid Agent key"
        super().__init__(self.message)
