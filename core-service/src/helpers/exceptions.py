class InternalException(Exception):
    """Internal exception"""


class UnknownObject(InternalException):
    """Unknown permission object"""


class SESEmailsSendingExceptions(InternalException):
    def __init__(self, sent_emails_count: int, message_ids):
        self.sent_emails_count = sent_emails_count
        self.message_ids = message_ids
