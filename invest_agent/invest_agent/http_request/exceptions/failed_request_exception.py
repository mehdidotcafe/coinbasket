class FailedRequestException(Exception):
    """Exception raised for failed HTTP requests.

    Args:
        message (str): Error message.
        status_code (int, optional): HTTP status code. Defaults to None.
        response (str, optional): Response content. Defaults to None.
    """

    def __init__(self, status_code: int, response: str):
        super().__init__(
            f"Failed request with status code: {status_code}, response: {response}"
        )
        self.status_code = status_code
        self.response = response
