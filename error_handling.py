import logging
import random
import time
from functools import wraps

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def handle_error(re_raise=True, log_traceback=True, exc_type=Exception, tries=1, delay=0.0, backoff=1):
    def handler(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _tries = tries
            _delay = delay
            try:
                return func(*args, **kwargs)
            except exc_type as e:
                if log_traceback:
                    logger.exception(e)
                while _tries > 0:
                    _tries -= 1
                    time.sleep(delay)
                    _delay = _delay * backoff
                    try:
                        return func(*args, **kwargs)
                    except BaseException:
                        _tries -= 1
                if re_raise:
                    raise e
            except BaseException as e:
                raise e

        return wrapper

    return handler


class handle_error_context:
    def __init__(self, re_raise=True, log_traceback=True, exc_type=Exception):
        self.re_raise = re_raise
        self.log_traceback = log_traceback
        self.exc_type = exc_type

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            if self.log_traceback:
                logger.exception(exc_tb)
            if self.re_raise:
                raise exc_val
            if exc_type != self.exc_type:
                raise exc_val
        return self


@handle_error(re_raise=False)
def some_function():
    x = 1 / 0  # ZeroDivisionError


some_function()
print(1)


@handle_error(re_raise=False, exc_type=KeyError)
def some_function():
    x = 1 / 0  # ZeroDivisionError


some_function()
print(1)


@handle_error(re_raise=True, tries=3, delay=0.5, backoff=2)
def some_function():
    if random.random() < 0.75:
        x = 1 / 0  # ZeroDivisionError


some_function()

with handle_error_context(log_traceback=True, exc_type=ValueError):
    raise ValueError()
