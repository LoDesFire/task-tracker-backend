from enum import StrEnum


class JWTTokenType(StrEnum):
    """
    Types of JWT tokens issued by the Auth Microservice
    """

    ACCESS = "access"
    REFRESH = "refresh"


class RevokeTokensScope(StrEnum):
    ALL = "all"
    THE_TOKEN = "the-token"
    CURRENT_APP = "current-app"
    # TODO: App by it id
