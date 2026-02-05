from helpers.exceptions.base_exceptions import BaseAppException


class RepositoryException(BaseAppException):
    """Repository Exception"""

class RepositoryIntegrityException(BaseAppException):
    """Repository Integrity Exception"""

class RepositoryNotFoundException(BaseAppException):
    """Repository Not Found Exception"""