import time
from functools import wraps


class RetriesException(Exception):
    """Retries exception"""


def retry(exceptions, total_tries=4, initial_wait=0.5, backoff_factor=2, logger=None):
    def log(message: str, *args):
        if logger is None:
            return
        logger.warning(message, *args)

    def retry_decorator(func):
        @wraps(func)
        def func_with_retries(*args, **kwargs):
            _tries, _delay = total_tries + 1, initial_wait
            while True:
                try:
                    log("%s. try:", total_tries + 2 - _tries)
                    return func(*args, **kwargs)
                except exceptions as e:
                    _tries -= 1
                    print_args = args if args else "no args"
                    if _tries <= 1:
                        msg = str(
                            "Function: %s\n"
                            "Failed despite best efforts after %s tries.\n"
                            "args: %s, kwargs: %s"
                        )
                        log(
                            msg,
                            func.__name__,
                            total_tries,
                            str(print_args),
                            str(kwargs),
                        )
                        raise
                    msg = str(
                        "Function: %s\n"
                        "Exception: %s\n"
                        "Retrying in %s seconds!, "
                        "args: %s, kwargs: %s\n"
                    )
                    log(
                        msg, func.__name__, str(e), _delay, str(print_args), str(kwargs)
                    )
                    time.sleep(_delay)
                    _delay *= backoff_factor

        return func_with_retries

    return retry_decorator
