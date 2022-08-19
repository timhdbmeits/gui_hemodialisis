# Standard library modules.
import os
import logging
from functools import wraps

# Third party modules.

# Local modules

# Globals and constants variables.
HTTPBIN_BASE_URL = os.environ.get('HTTPBIN_BASE_URL')

logger = logging.getLogger('mosquito')

if not HTTPBIN_BASE_URL:
    HTTPBIN_BASE_URL = 'https://httpbin.org'

    logger.info(f'Fell back on {HTTPBIN_BASE_URL} for testing. Consider to run a local instance '
                f'of httpbin to increase testing performance.')


def httpbin(path=''):
    if not path.startswith('/'):
        path = f'/{path}'

    return f'{HTTPBIN_BASE_URL}{path}'


def pass_k_of_n(k, n, message=None):
    """
    Decorator for test case methods that let's a test pass if at least k of n runs pass. This adds
    some tolerance to e.g. time critical test cases but will still catch systematical errors.

    :param k: number of successful attempts to pass
    :type k: int
    :param n: max attempts
    :type n: int
    :param message: custom message to be attached to exception
    :type message: str
    :return: decorator
    :rtype: function
    """
    assert 0 < k <= n

    def decorator(test_method):
        @wraps(test_method)
        def method_wrapper(*args, **kwargs):
            failures = 0

            for i in range(n):
                try:
                    test_method(*args, **kwargs)

                except AssertionError as error:
                    failures += 1

                    # fails if goal cannot be achieved anymore
                    if failures > n - k:
                        if message:
                            orig_message = f'{error.args[0]} -- ' if error.args else ''
                            error.args = (f'{orig_message}{message.strip()}', *error.args[1:])

                        raise error

                # aborts if goal is achieved
                if i - failures >= k:
                    break

        return method_wrapper

    return decorator


time_critical = pass_k_of_n(
    k=2,
    n=3,
    message='Errors occuring while testing time critical components may be caused by slow '
            'execution e.g. due a high cpu load.'
)
