from src.helpers.exceptions.base_exceptions import BaseAppException


class RepositoryException(BaseAppException):
    """RepositoryException"""


class RedisRepositoryException(RepositoryException):
    """RedisRepositoryException"""


class RedisRepositoryAlreadyExistsException(RedisRepositoryException):
    """RedisRepositoryAlreadyExistsException"""


class RepositoryNotFoundException(RepositoryException):
    """RepositoryNotFoundException"""


class RepositoryNotCreatedException(RepositoryException):
    """RepositoryNotCreatedException"""


class RepositoryIntegrityError(RepositoryException):
    """RepositoryIntegrityError"""
