from src.helpers.exceptions.base_exception import BaseAppException


class ServiceException(BaseAppException):
    def __init__(self, internal_message, user_error):
        super().__init__(internal_message)
        self.user_error = user_error

    user_error: str


class RegistrationException(ServiceException):
    def __init__(self, user_error, internal_message="Registration failed"):
        super().__init__(internal_message, user_error)


class LoginException(ServiceException):
    def __init__(self, user_error, internal_message="Login failed"):
        super().__init__(internal_message, user_error)
