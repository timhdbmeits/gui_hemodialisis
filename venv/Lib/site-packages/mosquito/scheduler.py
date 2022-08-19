#!/usr/bin/env python3
from functools import wraps

# Third party modules.

# Local modules
from mosquito.utils import MosquitoError
from mosquito.swarm import Session, Swarm

# Globals and constants variables.


class Scheduler:
    """
    Offers an interface similar to `requests.Session` but schedules all requests to a pool of
    sessions, the so called "swarm". Also it allows to be more obstinate and repeats requests on
    failure.
    """
    def __init__(self, swarm, max_attempts=1, repeat_on=None, session_timeout=None):
        """

        :param swarm: swarm instance
        :type swarm: Swarm
        :param max_attempts: maximum repetitions for requests on given errors
        :type max_attempts: int
        :param repeat_on: error codes where requests are repeated
        :param session_timeout: max time to wait for session to be used
        :type session_timeout: float
        """
        self._swarm = swarm
        self._max_attempts = int(max_attempts)
        self._repeat_on = tuple(repeat_on) if repeat_on else ()
        self._session_timeout = session_timeout

        assert self._max_attempts > 0, f'"max_attempts" has to be a positive integer.'
        assert 200 not in self._repeat_on, 'It does not make sense to repeat on status 200'

    swarm = property(fget=lambda self: self._swarm)
    max_attempts = property(fget=lambda self: self._max_attempts)
    repeat_on = property(fget=lambda self: tuple(self._repeat_on))

    def _request(self, request_method, url, **kwargs):
        for i in range(1, self._max_attempts + 1):
            with self._swarm.session(self._session_timeout) as session:
                response = request_method(session, url, **kwargs)

            status_code = response.status_code

            # repeat if status code is whitelisted
            if status_code in self._repeat_on:
                continue

            # return response on success
            elif status_code == 200:
                return response

            raise MosquitoError(f'request failed with code {status_code} on {i} attempt')

        raise MosquitoError(f'request failed after {self._max_attempts} attempts')

    @wraps(Session.get)
    def get(self, *args, **kwargs):
        return self._request(Session.get, *args, **kwargs)

    @wraps(Session.options)
    def options(self, *args, **kwargs):
        return self._request(Session.options, *args, **kwargs)

    @wraps(Session.head)
    def head(self, *args, **kwargs):
        return self._request(Session.head, *args, **kwargs)

    @wraps(Session.post)
    def post(self, *args, **kwargs):
        return self._request(Session.post, *args, **kwargs)

    @wraps(Session.put)
    def put(self, *args, **kwargs):
        return self._request(Session.put, *args, **kwargs)

    @wraps(Session.patch)
    def patch(self, *args, **kwargs):
        return self._request(Session.patch, *args, **kwargs)

    @wraps(Session.delete)
    def delete(self, *args, **kwargs):
        return self._request(Session.delete, *args, **kwargs)
