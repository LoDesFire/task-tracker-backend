from src.helpers.exceptions.service_exceptions import ServiceException


class AdminServiceException(ServiceException):
    def __init__(self, user_error, internal_message="Admin service exception"):
        super().__init__(internal_message, user_error)


class AdminUserNotFoundException(AdminServiceException):
    def __init__(self, user_error, internal_message="User not found"):
        super().__init__(internal_message, user_error)
