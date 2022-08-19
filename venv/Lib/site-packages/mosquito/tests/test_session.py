# Standard library modules.
from itertools import repeat
from unittest import TestCase
from collections import Counter

# Third party modules.
import requests

# Local modules
from mosquito import MosquitoError
from mosquito.session import Session, SessionObserver, IdentityFactory, SessionFactory
from mosquito.tests.utils import httpbin

# Globals and constants variables.


class TestSession(TestCase):
    def test_id(self):
        sessions = [Session() for _ in range(5)]

        for i, session in enumerate(sessions):
            self.assertEqual(i, session.id - sessions[0].id)

    def test_update(self):
        # 1. update attributes via kwargs
        # 2. update attributes via args
        # 3. update attributes via both, demonstrating that kwargs dominate
        # 4. update attributes via args using mapping
        args_l = [
            (),
            (dict(headers=dict(foo=42), max_redirects=42.0, auth=('foo', 'bar')),),
            (dict(headers=dict(foo=13), max_redirects=37.0, auth=('bar', 'foo')),),
            ((('headers', dict(foo=42)), ('max_redirects', 42.0), ('auth', ('foo', 'bar')),), )
        ]
        kwargs_l = [
            dict(headers=dict(foo=42), max_redirects=42.0, auth=('foo', 'bar')),
            {},
            dict(headers=dict(foo=42), max_redirects=42.0, auth=('foo', 'bar')),
            {}
        ]

        for args, kwargs in zip(args_l, kwargs_l):
            s = Session()
            s.update(*args, **kwargs)

            self.assertIn('foo', s.headers)
            self.assertIn('user-agent', s.headers)
            self.assertEqual(42, s.headers.get('foo'))

            self.assertIs(int, type(s.max_redirects))
            self.assertEqual(42, s.max_redirects)

            self.assertEqual(('foo', 'bar'), s.auth)

            with self.assertRaises(AttributeError):
                s.update(foo=42)

        s = Session()
        # invalid type of positional argument
        with self.assertRaises(TypeError):
            s.update((None,))

    def test_request(self):
        with Session() as session:
            observer = SessionObserver()
            session.register_observer(observer)

            _ = session.get(httpbin('/get'))

            self.assertEqual(1, observer.count)
            self.assertEqual(1, session.observer.count)


class TestSessionObserver(TestCase):
    @staticmethod
    def generate_response(status_code=200):
        response = requests.Response()

        response.status_code = status_code

        return response

    def test_update_reset(self):
        sessions = [Session() for _ in range(3)]
        sm = SessionObserver()

        for i in range(10):
            sm.update(sessions[i % 3], self.generate_response((i % 2 * 100 + 200)))

        self.assertEqual(10, sm.count)
        self.assertEqual(0., sm.duration)
        self.assertEqual([3, 3, 4], sorted(sm.sessions.values()))
        self.assertEqual(Counter({200: 5, 300: 5}), sm.status_codes)

        sm.reset()

        self.assertEqual(0, sm.count)
        self.assertEqual(0., sm.duration)
        self.assertEqual(Counter(), sm.sessions)
        self.assertEqual(Counter(), sm.status_codes)


class TestIdentityFactory(TestCase):
    def test_identities(self):
        def val():
            return [42]

        if_1 = IdentityFactory({})
        if_2 = IdentityFactory({attr: vals for attr, vals in zip(Session.__attrs__, repeat(val))})
        if_3 = IdentityFactory({attr: vals for attr, vals in zip(Session.__attrs__, repeat(val))},
                               require=Session.__attrs__)
        if_4 = IdentityFactory(dict(foo=[42]))
        if_5 = IdentityFactory({}, require=['fnord'])
        if_6 = IdentityFactory({}, require=['headers'])
        if_7 = IdentityFactory(dict(identities=[dict(headers=dict(foo=42))]), require=['headers'])
        if_8 = IdentityFactory(dict(headers=[dict(foo=42)]), require=['headers'])

        self.assertEqual([{}], list(if_1))

        for im in (if_2, if_3):
            self.assertEqual(set(Session.__attrs__), set(list(im)[0].keys()))
            self.assertEqual({42}, set(list(im)[0].values()))

        with self.assertRaises(AttributeError):
            _ = list(if_4)

        with self.assertRaises(AttributeError):
            _ = list(if_5)

        with self.assertRaises(MosquitoError):
            _ = list(if_6)

        self.assertEqual([dict(headers=dict(foo=42))], list(if_7))
        self.assertEqual([dict(headers=dict(foo=42))], list(if_8))


class TestSessionFactory(TestCase):
    def setUp(self):
        self.factory_class = SessionFactory

    def test_sessions(self):
        attributes = dict(params=(dict(foo=i) for i in range(3)))
        sessions = tuple(SessionFactory(attributes))

        self.assertEqual(3, len(sessions))
        for i, session in enumerate(sessions):
            self.assertEqual(dict(foo=i), session.params)
            self.assertIsInstance(session, Session)
