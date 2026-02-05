from helpers.exceptions.base_exceptions import BaseAppException


class ServiceException(BaseAppException):
    """Repository Exception"""

class ServiceNotFoundException(BaseAppException):
    """Repository Not Found Exception"""