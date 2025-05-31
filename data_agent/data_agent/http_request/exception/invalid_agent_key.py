class InvalidAgentKey(Exception):
    """Exception raised for invalid API key errors."""

    def __init__(self):
        self.message = "Invalid Agent key"
        super().__init__(self.message)
