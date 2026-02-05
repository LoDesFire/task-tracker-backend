from src.helpers.exceptions.base_exceptions import BaseAppException


class ServiceException(BaseAppException):
    def __init__(self, internal_message, user_error):
        super().__init__(internal_message)
        self.user_error = user_error

    user_error: str


class AuthServiceException(ServiceException):
    """AuthServiceException"""


class JWTServiceException(ServiceException):
    def __init__(self, user_error=None, internal_message="JWT action failed"):
        super().__init__(internal_message, user_error)
