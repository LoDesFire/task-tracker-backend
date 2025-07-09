class BaseAppException(Exception):
    def __init__(self, message: str | None = None):
        self.message = message

    def __str__(self):
        return self.message
