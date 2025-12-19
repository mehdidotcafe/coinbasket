from typing import Any


class AppException(Exception):
    status_code: int
    message: str
    details: dict[str, Any] | None

    def __init__(
        self,
        status_code: int,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.status_code = status_code
        self.message = message
        self.details = details
