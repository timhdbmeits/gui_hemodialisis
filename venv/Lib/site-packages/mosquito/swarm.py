# Standard library modules.
from queue import Empty
from threading import Lock
from contextlib import contextmanager

# Third party modules.

# Local modules
from mosquito.utils import logger, evaluate, MosquitoError, DelayQueue, SingletonContextABC
from mosquito.session import Session, SessionObserver, SessionFactory

# Globals and constants variables.


class Swarm(SingletonContextABC):
    """
    A swarm is a collection of request sessions that manages initialisation, teardown and access to
    those. Note that there exists only one swarm at a time and manipulation of the swarm object only
    has effects if no swarm context is active.
    """
    __attrs__ = ['on_init', 'on_close', 'delay', 'require', *SessionFactory.__attrs__]
    observer = SessionObserver()

    def __init__(self, delay=0., on_init=None, on_close=None, require=None, **session_attributes):
        """
        :param delay: delay for each session that determines max request frequency
        :type delay: float
        :param on_init: call back function to initialize sessions
        :param on_close: call back function to tear down sessions
        :param require: a list of attributes that have to be provided to each session
        :param session_attributes: session attributes
        """
        self._delay = delay
        self._on_init = on_init
        self._on_close = on_close
        self._session_factory = SessionFactory(session_attributes, require)
        self._lock = Lock()
        self._sessions = None
        self._size = 0

    def __len__(self):
        """Counts items in session queue."""
        with self._lock:
            return self._size

    @contextmanager
    def session(self, timeout=None):
        """
        A context that provides the next available session object. If time passed since the last
        time using that session is less than :attr:`delay` this method blocks.

        :param timeout: max time to wait for session
        :return: session
        :rtype: Session
        """
        if self._sessions is None:
            raise MosquitoError('sessions are available in open swarm context only')

        session = self._sessions.get(timeout=timeout)

        try:
            yield session

        finally:
            self._sessions.put(session)

    def __on_open__(self):
        """Initialize sessions."""
        self._sessions = DelayQueue(delay=evaluate(self._delay))

        for session in self._session_factory:
            session.register_observer(self.observer)

            if self._on_init:
                self._on_init(session)

            self._size += 1
            self._sessions.put(session)

        logger.debug(f'opened swarm with {len(self)} sessions')

    def __on_close__(self):
        """Close all sessions."""
        try:
            while True:
                session = self._sessions.get_nowait()

                if self._on_close:
                    self._on_close(session)

                session.close()

        except Empty:
            pass

        self._size = 0
        self._sessions = None
        logger.debug(f'closed swarm successfully')
