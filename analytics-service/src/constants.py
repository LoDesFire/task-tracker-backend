from enum import StrEnum


class JWTTokenType(StrEnum):
    """
    Types of JWT tokens issued by the Auth Microservice
    """

    ACCESS = "access"
    REFRESH = "refresh"
