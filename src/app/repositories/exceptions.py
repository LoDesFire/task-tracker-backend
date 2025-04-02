from src.app.exceptions import BaseApplicationException


class RepositoryException(BaseApplicationException):
    pass


class RepositoryNotFoundException(RepositoryException):
    pass


class RepositoryNotCreatedException(RepositoryException):
    pass


class RepositoryIntegrityError(RepositoryException):
    pass
