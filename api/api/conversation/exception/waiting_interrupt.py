from api.shared.app_exception import AppException


class WaitingInterrupt(AppException):
    def __init__(
        self, message: str = "There is an active interrupt. Please resume first."
    ):
        super().__init__(422, message)
