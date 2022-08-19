# Standard library modules.
import abc
import sys
import queue
import logging
from functools import wraps
from time import time, sleep
from threading import Lock, RLock
from contextlib import contextmanager

# Third party modules.
from tqdm.autonotebook import tqdm

# Local modules

# Globals and constants variables.
FORMAT_STRING = '{asctime}  {threadName:<12}  {levelname:>8}:  {message}'

handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(logging.Formatter(FORMAT_STRING, style='{'))

logger = logging.getLogger('mosquito')
logger.addHandler(handler)


class MosquitoError(Exception):
    """mosquito specific error"""


def format_list(s, quote_char=''):
    if len(s) == 0:
        return ''

    s = sorted(f'{quote_char}{str(item)}{quote_char}' for item in s)

    if len(s) == 1:
        return s[0]

    *s, last = s

    return ', '.join(s) + f' and {last}'


def args_to_kwargs(_func=None, ftype='function', keep=0):
    """
    Decorator for functions and (static, class-) methods that converts positional arguments into key
    word arguments.

    :param _func: function or method to decorate
    :param ftype: type of function, one of: `function`, `static`, `method` and `classmethod`
    :type ftype: string
    :param keep: number of positional arguments that will be forwarded rather than evaluated.
    :type keep: int
    :return: decorator or a wrapper if function is specified
    """
    kw_func_like = {'function', 'static'}
    kw_meth_like = {'method', 'classmethod'}
    kw_all = {*kw_func_like, *kw_meth_like}

    # validate function type
    assert ftype in kw_all, f'`method` has to be one of {kw_all}!'

    # compute offset for positional arguments to be evaluated, default is 0 (evaluate all)
    offset = (1 if ftype in kw_meth_like else 0) + keep

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # split args in those that are kept and those, that are used to update kwargs
            keep = args[:offset]
            args = args[offset:]

            # update kwarg args with what was found in
            for i in range(len(args)):
                arg_dict = dict(args[-i - 1])
                arg_dict.update(kwargs)
                kwargs = arg_dict

            return func(*keep, **kwargs)

        return wrapper

    if _func:
        return decorator(_func)

    return decorator


def evaluate(value, *args, **kwargs):
    """
    This is a helper function used for lazy evaluation.

        1. If value is a callable it's called with given parameters
        2. If value is an iterable is converted to a tuple

    :param value: value to evluate
    :param args: positional arguments that are passed if value is a callable
    :param kwargs: key word arguments that are passed if value is a callable
    :return: evaluate value
    """
    if callable(value):
        value = value(*args, **kwargs)

    try:
        return tuple(value)

    except TypeError:
        return value


def monitor_queue(qclass):
    """
    Decorator that wraps any queue class in order to observer its progress using tqdm.

    :param qclass: queue class
    :return: monitored wrapper for given queue class
    """
    class _MonitoredQueue(qclass):
        @wraps(qclass.__init__)
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._monitor = None
            self._monitor_lock = Lock()

        @contextmanager
        def tqdm(self, *args, **kwargs):
            """
            Opens a progress observer that keeps track of queue tasks.

            :param args: positional arguments for tqdm
            :param kwargs: key word arguments for tqdm
            :return: tqdm progress observer
            :rtype: tqdm
            """
            try:
                with self._monitor_lock:
                    self._monitor = tqdm(*args, **kwargs)
                yield self._monitor

            finally:
                with self._monitor_lock:
                    self._monitor.close()
                    self._monitor = None

        @wraps(qclass.task_done)
        def task_done(self):
            with self._monitor_lock:
                if self._monitor is not None:
                    self._monitor.update(1)

            super().task_done()

    _MonitoredQueue.__name__ = f'Monitored{qclass.__name__}'
    _MonitoredQueue.__doc__ = qclass.__doc__

    return _MonitoredQueue


@monitor_queue
class MonitoredQueue(queue.Queue):
    """monitored queue"""


class DelayQueue(queue.PriorityQueue):
    """
    A FIFO queue that ensures each item remains for a minimum amount of time in it.
    """
    def __init__(self, delay=0., maxsize=0):
        """
        :param delay: minimum time each item has to remain in queue
        :type delay: float
        :param maxsize: maximum size for queue
        :type maxsize: int
        """
        super().__init__(maxsize)

        assert delay >= 0, 'delay must not be negative'
        self._delay = delay

    @property
    def delay(self):
        return self._delay

    @wraps(queue.PriorityQueue.put)
    def put(self, item, *args, **kwargs):
        super().put((time(), item), *args, **kwargs)

    @wraps(queue.PriorityQueue.get)
    def get(self, *args, **kwargs):
        timestamp, item = super().get(*args, **kwargs)

        sleep(max(0, evaluate(self._delay) - (time() - timestamp)))

        return item


@monitor_queue
class MonitoredDelayQueue(DelayQueue):
    """monitored delay queue"""


class NameSpaceDict(dict):
    """A dictionary class whose arguments can be accessed as attributes."""
    @staticmethod
    def _mapping(*args, **kwargs):
        state = {}

        for arg in args:
            state.update(arg)

        state.update(kwargs)

        for key, value in state.items():
            yield key, NameSpaceDict(value) if isinstance(value, dict) else value

    def __init__(self, *args, **kwargs):
        super().__init__(self._mapping(*args, **kwargs))

    def __setitem__(self, key, value):
        super().__setitem__(key, NameSpaceDict(value) if isinstance(value, dict) else value)

    def __getattr__(self, item):
        try:
            return self.__getitem__(item)

        except KeyError as error:
            raise AttributeError(error)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)


class SingletonMeta(type):
    """
    This meta class ensures that there exists only one instance of its instances at a time. It's
    safe to instantiate it multiple times.
    """
    @wraps(type.__init__)
    def __init__(cls, name, bases, dct):
        super(SingletonMeta, cls).__init__(name, bases, dct)

        _new = cls.__new__

        @wraps(cls.__new__)
        def _new_wrapper(kls, *_, **__):
            if kls.instance is None:
                kls.instance = _new(kls)
            return kls.instance

        cls.instance = None
        cls.__new__ = classmethod(_new_wrapper)

    def __call__(self, *args, **kwargs):
        """ensure __init__ is only called once"""
        if self.instance is None:
            self.__new__(*args, **kwargs).__init__(*args, **kwargs)

        return self.instance


class SingletonABCMeta(SingletonMeta, abc.ABCMeta):
    """Mixin for `abc.ABCMeta` and `SingletonMeta`"""


class SingletonContextABC(metaclass=SingletonABCMeta):
    """
    This class combines two popular programming patterns: singleton and context manager. The
    singleton property ensures that there's always one instance at most of this class unless you
    break that mechanism intentionally by calling :meth:`detach()`.
    As the context may be entered multiple times e.g. by nesting `with` statements or accessing that
    instance from multiple threads it keeps track of how often it is open. When the context is
    entered for the first and left for the last time a corresponding callback method is toggled.

    In order to implement the singleton context protocol you may overwrite the following callback
    methods:

      * :meth:`__on__open__(self) -> None`
      * :meth:`__on__close__(self) -> None`

    """
    __ctx_lock = RLock()
    __ctx_counter = 0

    def __new__(cls):
        """
        To prevent instantiation of this class without having abstract methods we perform a manual
        check.

        :return: new instance
        :rtype: SingletonContextABC
        """
        if cls is SingletonContextABC:
            raise TypeError(f'Can\'t instantiate abstract class {cls.__name__}.')

        return object.__new__(cls)

    def __setattr__(self, key, value):
        """
        The object can be modified as long as no context is open. Once that's the case calling this
        method won't have an effect anymore and fails silently.

        :param key: attribute name
        :type key: str
        :param value: new attribute value
        """
        with type(self).__ctx_lock:
            if not self.active():
                super().__setattr__(key, value)

            else:
                logger.debug(f'try to modify "{key}" of open singleton context')

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @classmethod
    def is_open(cls):
        """
        Counts how often the context was opened and not yet closed.

        :return: Value of internal context counter.
        :rtype: int
        """
        return cls.__ctx_counter

    @classmethod
    def active(cls):
        """
        Check whether any context is active

        :return: true if any context is active
        :rtype: bool
        """
        return cls.is_open() != 0

    @classmethod
    def detach(cls):
        """
        As this class implements the singleton pattern it holds a reference to its only instance
        internally. Also it has a counter that tracks how often the context is open currently. Both
        are reset by this method and it may happen that multiple instances of this class exist.

        .. warning:: Calling this method may have unexpected side effects!
        """
        if cls.instance is not None:
            logger.debug(f'Detaching {cls.instance}. This may have unexpected side effects!')

            with cls.__ctx_lock:
                cls.__ctx_counter = 0

                del cls.instance
                cls.instance = None

    def __on_open__(self):
        """
        Callback method that is triggered when the context is entered for the first time or was
        closed before.
        """
        pass

    def __on_close__(self):
        """Callback method that is triggered when the context is left for the last time."""
        pass

    def open(self):
        """Opens the singleton context."""
        cls = type(self)

        with cls.__ctx_lock:
            if cls.__ctx_counter == 0:
                self.__on_open__()

            cls.__ctx_counter += 1

    def close(self):
        """Closes the singleton context."""
        cls = type(self)

        with cls.__ctx_lock:
            # This check is necessary for cases where a thread crashes during the call of
            # `__on_open__` and therefore enters this method without incrementing the context
            # counter before.
            if cls.__ctx_counter > 0:
                cls.__ctx_counter -= 1

                if cls.__ctx_counter == 0:
                    self.__on_close__()
