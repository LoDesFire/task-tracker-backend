from src.helpers.exceptions.base_exceptions import BaseAppException


class HelpersException(BaseAppException):
    """HelpersException"""


class JWTDecodeException(HelpersException):
    """JWTDecodeException"""
