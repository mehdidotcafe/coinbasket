from api.shared.app_exception import AppException


class InvalidSignature(AppException):
    def __init__(self, message: str = "Invalid signature"):
        super().__init__(401, message)
