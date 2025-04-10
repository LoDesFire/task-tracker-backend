from src.helpers.exceptions.service_exceptions.base_exceptions import (
    AuthServiceException,
)


class RegistrationException(AuthServiceException):
    def __init__(self, user_error, internal_message="Registration failed"):
        super().__init__(internal_message, user_error)


class LoginException(AuthServiceException):
    def __init__(self, user_error, internal_message="Login failed"):
        super().__init__(internal_message, user_error)


class RevokeException(AuthServiceException):
    def __init__(self, user_error, internal_message="Tokens revoke failed"):
        super().__init__(internal_message, user_error)


class VerificationException(AuthServiceException):
    def __init__(self, user_error, internal_message="Verification failed"):
        super().__init__(internal_message, user_error)


class RefreshingException(AuthServiceException):
    def __init__(self, user_error, internal_message="Refreshing failed"):
        super().__init__(internal_message, user_error)
