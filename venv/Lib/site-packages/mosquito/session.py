# Standard library modules.
from threading import Lock
from itertools import count
from functools import wraps
from collections import Counter

# Third party modules.
import requests

# Local modules
from mosquito.utils import logger, format_list, evaluate, args_to_kwargs, MosquitoError

# Globals and constants variables.


class Session(requests.Session):
    """
    Monitorable session object
    """
    __id_counter = count()

    def __init__(self, **kwargs):
        """
        :param kwargs: attributes to be set (see :meth:`update`)
        """
        super().__init__()

        self._id = next(self.__id_counter)
        self._observer = SessionObserver()
        self._observers = [self.observer]
        self._explicitly_set = sorted(kwargs.keys())

        self.update(kwargs)

    def __str__(self):
        return f'{self.__class__.__name__}(id={self.id})'

    def __repr__(self):
        attrs = ', '.join(f'{k}={getattr(self, k, "")}' for k in ['id'] + self._explicitly_set)
        return f'{self.__class__.__name__}({attrs})'

    @property
    def id(self):
        return self._id

    @property
    def observer(self):
        return self._observer

    @args_to_kwargs(ftype='method')
    def update(self, **kwargs):
        """
        Patch attributes of a session. Dict like attributes will be updated. Other attributes are
        casted if possible and then set.

        :param kwargs: attributes to be updated
        """
        for name, value in kwargs.items():
            if name not in self.__attrs__:
                raise AttributeError(
                    f'\'{self.__class__.__name__}\' object has no attribute \'{name}\''
                )

            attr_t = type(getattr(self, name, None))

            # update dict like attributes (dict, cookie jar, ...)
            if hasattr(attr_t, 'update'):
                getattr(self, name).update(value)
                continue

            # set (casted) value
            try:
                setattr(self, name, attr_t(value))

            except TypeError:
                setattr(self, name, value)

    def register_observer(self, observer):
        """
        Attach observer to session.

        :param observer: a session observer instance
        :type observer: SessionObserver
        """
        self._observers.append(observer)

    @wraps(requests.Session.request)
    def request(self, method, url, *args, **kwargs):
        logger.debug(f'{self}: {method} {url}')
        response = super().request(method, url, *args, **kwargs)

        for observer in self._observers:
            observer.update(self, response)

        return response


class SessionObserver:
    """An observer for sessions that collects request statistics."""
    def __init__(self):
        self._lock = Lock()

        self.count = None
        self.duration = None
        self.sessions = None
        self.status_codes = None

        self.reset()

    def __str__(self):
        mean_duration = self.duration / (self.count or 1)
        return \
            f'{self.__class__.__name__}(' \
            f'count={self.count}, ' \
            f'mean_duration={mean_duration:.5f}s, ' \
            f'sessions={self.sessions}, ' \
            f'status_codes={self.status_codes}' \
            f')'

    def reset(self):
        """Reset session observer."""
        with self._lock:
            self.count = 0
            self.duration = 0
            self.sessions = Counter()
            self.status_codes = Counter()

    def update(self, session, response):
        """
        Update session statistics.

        :param session: session object
        :type session: Session
        :param response: response object
        :type response: requests.Response
        """
        with self._lock:
            self.count += 1
            self.duration += response.elapsed.total_seconds()
            self.sessions.update([session.id])
            self.status_codes.update([response.status_code])


class IdentityFactory:
    """Generate session identities from given attributes."""
    __attrs__ = ['identities', *Session.__attrs__]

    def __init__(self, attributes, require=None):
        """
        :param attributes: attributes to generate identities from, usually a dictionary where keys
                           are attribute names and values that evaluate to iterables with actual
                           attribute values
        :param require: container with keys of mandatory attributes
        """
        self._attributes = attributes
        self._require = require

    @staticmethod
    def _identity_generator(attributes):
        if attributes:
            keys, values = zip(*attributes.items())

            for vals in zip(*values):
                identity = dict(zip(keys, vals))
                identity.update(identity.pop('identities', {}))

                yield identity

        else:
            yield {}

    def __iter__(self):
        # evaluate and validate requirements
        available_attrs = set(Session.__attrs__)
        requirements = set(evaluate(self._require) or ())

        if not requirements.issubset(available_attrs):
            unknown = format_list(available_attrs - requirements, quote_char='"')
            raise AttributeError(f'unknown requirements: {unknown}')

        # evaluate all attributes
        attributes_dict = {attr: evaluate(value) for attr, value in self._attributes.items()} or {}

        # generate identities
        for identity in self._identity_generator(attributes_dict):
            attrs = set(identity.keys())

            if not requirements.issubset(attrs):
                missing = format_list(requirements - attrs, quote_char='"')
                raise MosquitoError(f'requirements {missing} not fulfilled')

            if not attrs.issubset(available_attrs):
                unknown = format_list(attrs - available_attrs, quote_char='"')
                raise AttributeError(f'unknown attributes: {unknown}')

            yield identity


class SessionFactory(IdentityFactory):
    """Generate request sessions from given attributes."""
    def __iter__(self):
        for attributes in super().__iter__():
            yield Session(**attributes)
