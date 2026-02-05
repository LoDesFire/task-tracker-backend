from src.helpers.exceptions.service_exceptions import ServiceException


class UserServiceException(ServiceException):
    def __init__(self, user_error, internal_message="User service exception"):
        super().__init__(internal_message, user_error)


class UserNotFoundException(UserServiceException):
    def __init__(self, user_error, internal_message="User not found"):
        super().__init__(internal_message, user_error)
