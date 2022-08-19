#!/usr/bin/env python3
# Standard library modules.
import queue
from time import time, sleep
from unittest import TestCase
from statistics import median

# Third party modules.

# Local modules
from mosquito.utils import (
    format_list, args_to_kwargs, evaluate, monitor_queue, MonitoredQueue, DelayQueue, NameSpaceDict,
    SingletonMeta, SingletonContextABC
)
from mosquito.tests.utils import pass_k_of_n, time_critical

# Globals and constants variables.


class TestFunctions(TestCase):
    def test_format_list(self):
        self.assertEqual('', format_list([]))
        self.assertEqual('1', format_list([1]))
        self.assertEqual('1 and 2', format_list([1, 2]))
        self.assertEqual('1 and 2', format_list([2, 1]))
        self.assertEqual('1, 2 and 3', format_list([1, 3, 2]))
        self.assertEqual('"1", "2" and "3"', format_list([1, 3, 2], quote_char='"'))

    def test_k_of_n(self):
        # check logical correctness
        for k, n in [(2, 3), (2, 4), (3, 5)]:
            for i in range(2**n):
                # integer to bit tuple (big endian)
                ibit = tuple((i >> j) & 1 for j in range(n))

                states = iter(ibit)

                @pass_k_of_n(k, n)
                def test_mock():
                    assert next(states)

                if sum(ibit) >= k:
                    test_mock()

                else:
                    with self.assertRaises(AssertionError):
                        test_mock()

        # check if message wrapping works
        @pass_k_of_n(1, 1, 'fnord')
        def test_mock(msg=None):
            if msg:
                assert False, msg

            assert False

        # custom message only
        try:
            test_mock()
            self.fail()

        except AssertionError as error:
            self.assertNotIn('--', str(error))
            self.assertIn('fnord', str(error))

        # merging original and custom message
        try:
            test_mock('foo')
            self.fail()

        except AssertionError as error:
            self.assertIn('foo --', str(error))
            self.assertIn('fnord', str(error))

    def test_args_as_kwargs(self):
        @args_to_kwargs
        def mock(*args, **kwargs):
            return args, kwargs

        class Mock:
            @args_to_kwargs
            def static_1(*args, **kwargs):
                return args, kwargs

            @staticmethod
            @args_to_kwargs(ftype='static')
            def static_2(*args, **kwargs):
                return args, kwargs

            @args_to_kwargs(ftype='method')
            def method(self, *args, **kwargs):
                return args, kwargs

            @classmethod
            @args_to_kwargs(ftype='classmethod')
            def classmethod(cls, *args, **kwargs):
                return args, kwargs

            @args_to_kwargs(ftype='method', keep=3)
            def keep(self, a, b, c, *args, **kwargs):
                return a, b, c, args, kwargs

            @args_to_kwargs
            def fail(self, *args, **kwargs):
                return args, kwargs

        with self.assertRaises(AssertionError):
            @args_to_kwargs(ftype='foo')
            def foo():
                pass

        funcs = (mock, Mock.static_1, Mock.static_2, Mock.method, Mock.classmethod)
        args = ((), (), (), (Mock(),), ())

        for func, arg in zip(funcs, args):
            args, kwargs = func(*arg)
            self.assertEqual((), args)
            self.assertEqual({}, kwargs)

            # key word arguments are kept
            args, kwargs = func(*arg, foo=42)
            self.assertEqual((), args)
            self.assertEqual(dict(foo=42), kwargs)

            # positional argument is converted to key word arguments
            args, kwargs = func(*arg, dict(foo=42))
            self.assertEqual((), args)
            self.assertEqual(dict(foo=42), kwargs)

            # key word arguments dominate positional arguments
            args, kwargs = func(*arg, dict(foo=1337), foo=42)
            self.assertEqual((), args)
            self.assertEqual(dict(foo=42), kwargs)

            # right most argument dominates
            args, kwargs = func(*arg, dict(foo=1337), dict(foo=42))
            self.assertEqual((), args)
            self.assertEqual(dict(foo=42), kwargs)

            # multiple positional arguments
            args, kwargs = func(*arg, dict(foo=13), dict(foo=37), foo=42)
            self.assertEqual((), args)
            self.assertEqual(dict(foo=42), kwargs)

            # it also works with mappings
            args, kwargs = func(*arg, (('foo', 42),))
            self.assertEqual((), args)
            self.assertEqual(dict(foo=42), kwargs)

            # error when positional argument is not a dict like
            with self.assertRaises(TypeError):
                func(*arg, None)

        # first three positional arguments are kept
        a, b, c, args, kwargs = Mock().keep(13, 37, 42, dict(foo=42), bar=1337)
        self.assertEqual(13, a)
        self.assertEqual(37, b)
        self.assertEqual(42, c)
        self.assertEqual((), args)
        self.assertEqual(dict(foo=42, bar=1337), kwargs)

        # wrong decorator parametrisation results in error
        with self.assertRaises(TypeError):
            Mock().fail()

    def test_evaluate(self):
        self.assertEqual(None, evaluate(None))
        self.assertTupleEqual((0, 1, 2), evaluate([0, 1, 2]))
        self.assertTupleEqual((0, 1, 2), evaluate(range(3)))
        self.assertTupleEqual((0, 1, 2), evaluate(lambda: [0, 1, 2]))
        self.assertTupleEqual((0, 1, 2), evaluate(lambda: range(3)))


class TestMonitorQueue(TestCase):
    def setUp(self):
        self.mq = MonitoredQueue()

        for i in range(3):
            self.mq.put(f'item_{i}')

    def test_monitor_queue(self):
        queue_class = monitor_queue(queue.Queue)

        self.assertIn('__init__', queue_class.__dict__)
        self.assertIn('tqdm', queue_class.__dict__)
        self.assertIn('task_done', queue_class.__dict__)

    def test_tqdm(self):
        with self.mq.tqdm() as monitor:
            for i in range(2):
                self.mq.get_nowait()
                self.mq.task_done()

                self.assertEqual(i+1, monitor.n)

    def test_task_done(self):
        self.assertEqual(3, self.mq.unfinished_tasks)

        self.mq.get_nowait()
        self.mq.task_done()

        self.assertEqual(2, self.mq.unfinished_tasks)


class TestNameSpaceDict(TestCase):
    def test___init__(self):
        nsd_1 = NameSpaceDict([('a', 13), ('b', 37)])
        nsd_2 = NameSpaceDict(a=13, b=37)
        nsd_3 = NameSpaceDict([('a', 13), ('b', 42)], b=37)
        nsd_4 = NameSpaceDict(foo=dict(bar=dict()))

        for nsd in [nsd_1, nsd_2, nsd_3]:
            self.assertEqual(nsd, NameSpaceDict(dict(a=13, b=37)))

        self.assertIsInstance(nsd_4.foo, NameSpaceDict)
        self.assertIsInstance(nsd_4.foo.bar, NameSpaceDict)

    def test_set(self):
        nsd = NameSpaceDict()

        nsd['a'] = 13
        nsd.b = 37
        nsd['foo'] = {}
        nsd.bar = {}

        self.assertEqual(nsd.a, 13)
        self.assertEqual(nsd.b, 37)

        self.assertIsInstance(nsd.foo, NameSpaceDict)
        self.assertIsInstance(nsd.bar, NameSpaceDict)

    def test_get(self):
        nsd = NameSpaceDict(fnord=42)

        self.assertEqual(nsd.fnord, 42)
        self.assertEqual(nsd['fnord'], 42)

        with self.assertRaises(KeyError):
            _ = nsd['foo']

        with self.assertRaises(AttributeError):
            _ = nsd.foo


class TestDelayQueue(TestCase):
    def test___init__(self):
        with self.assertRaises(AssertionError):
            _ = DelayQueue(delay=-1.)

    @time_critical
    def test_put_get_delay(self):
        n = 4
        t_unit = 3e-4
        delay = 5 * t_unit
        dq = DelayQueue(delay=delay)

        put_times = []
        get_times = []
        overheads = []

        for i in range(n):
            dq.put(i)
            put_times.append(time())

            sleep(t_unit)

        for i in range(n):
            j = dq.get()
            get_times.append(time())

            self.assertEqual(i, j)

        for put_time, get_time in zip(put_times, get_times):
            overheads.append(get_time - put_time - delay)
            self.assertLess(put_time, get_time)

        self.assertLess(median(overheads), 5e-4)


class TestSingletonABCMeta(TestCase):
    class SingletonMockA(metaclass=SingletonMeta):
        def __init__(self):
            pass

    class SingletonMockB(metaclass=SingletonMeta):
        def __init__(self):
            pass

    def test(self):
        s_1 = self.SingletonMockA()
        s_2 = self.SingletonMockA()
        s_3 = self.SingletonMockB()
        s_4 = self.SingletonMockB()

        self.assertIs(s_1, s_2)
        self.assertIs(s_3, s_4)
        self.assertIsNot(s_1, s_3)


class TestSingletonContext(TestCase):
    class MockError(Exception):
        pass

    class SingletonContextMock(SingletonContextABC):
        def __init__(self, fail_on_open=None, fail_on_close=None, **kwargs):
            self.fail_on_open = fail_on_open
            self.fail_on_close = fail_on_close
            self.ran_on_open = False
            self.ran_on_close = False
            self.init_ct = getattr(self, 'init_ct', 0) + 1

            for key, value in kwargs.items():
                setattr(self, key, value)

        def __on_open__(self):
            if self.fail_on_open:
                raise self.fail_on_open('failed on open')

            self.ran_on_open = True

        def __on_close__(self):
            if self.fail_on_close:
                raise self.fail_on_close('failed on close')

            self.ran_on_close = True

    def setUp(self):
        self.SingletonContextMock.detach()

    def test__init__(self):
        s_1 = self.SingletonContextMock(foo=42)
        s_2 = self.SingletonContextMock(foo=1337)

        self.assertIs(s_1, s_2)
        self.assertEqual(s_1.init_ct, 1)
        self.assertEqual(s_2.init_ct, 1)
        self.assertEqual(s_1.foo, 42)
        self.assertEqual(s_2.foo, 42)

    def test__new__(self):
        with self.assertRaises(TypeError):
            _ = SingletonContextABC()

    def test_setattr(self):
        s = self.SingletonContextMock()

        s.foo = 42
        self.assertEqual(42, s.foo)

        s.foo = 1337
        self.assertEqual(1337, s.foo)

        with s:
            s.foo = 42
            self.assertEqual(1337, s.foo)

        s.foo = 42
        self.assertEqual(42, s.foo)

    def test_context(self):
        # test for errors occurring on startup / teardown
        setups = ({}, dict(fail_on_open=self.MockError), dict(fail_on_close=self.MockError))
        for kwargs in setups:
            sc = self.SingletonContextMock(**kwargs)

            try:
                with sc:
                    self.assertEqual(1, sc.is_open())

            except self.MockError:
                if not kwargs.values():
                    self.fail('did not expect any errors to occur')

            self.assertEqual(0, sc.is_open())

            self.SingletonContextMock.detach()

        # test for errors occurring in poll
        sc = self.SingletonContextMock()
        with self.assertRaises(self.MockError):
            with sc:
                raise self.MockError()

        self.assertEqual(0, sc.is_open())

    def test_is_open(self):
        sc = self.SingletonContextMock()

        self.assertEqual(0, sc.is_open())

        with self.SingletonContextMock():
            self.assertEqual(1, sc.is_open())

            with self.SingletonContextMock():
                self.assertEqual(2, sc.is_open())

                with self.SingletonContextMock():
                    self.assertEqual(3, sc.is_open())

                self.assertEqual(2, sc.is_open())

            self.assertEqual(1, sc.is_open())

        self.assertEqual(0, sc.is_open())

    def test_active(self):
        sc = self.SingletonContextMock()

        self.assertFalse(sc.active())

        with self.SingletonContextMock():
            self.assertTrue(sc.active())

            with self.SingletonContextMock():
                self.assertTrue(sc.active())

            self.assertTrue(sc.active())

        self.assertFalse(sc.active())

    def test_detach(self):
        self.assertIsNone(self.SingletonContextMock.instance)

        with self.SingletonContextMock():
            pass

        self.assertIsNotNone(self.SingletonContextMock.instance)

        self.SingletonContextMock.detach()

        self.assertIsNone(self.SingletonContextMock.instance)

    def test_open_close_manual(self):
        sc = self.SingletonContextMock()

        self.assertFalse(sc.ran_on_open)
        self.assertFalse(sc.ran_on_close)

        sc.open()

        self.assertTrue(sc.ran_on_open)
        self.assertFalse(sc.ran_on_close)

        sc.close()

        self.assertTrue(sc.ran_on_open)
        self.assertTrue(sc.ran_on_close)

    def test_open_close_auto(self):
        sc = self.SingletonContextMock()

        self.assertFalse(sc.ran_on_open)
        self.assertFalse(sc.ran_on_close)

        with sc:
            pass

        self.assertTrue(sc.ran_on_open)
        self.assertTrue(sc.ran_on_close)
