# Standard library modules.
from time import time
from math import isclose
from unittest import TestCase
from queue import Empty

# Third party modules.

# Local modules
from mosquito import MosquitoError, Swarm
from mosquito.tests.utils import time_critical

# Globals and constants variables.


class TestSwarm(TestCase):
    def setUp(self):
        Swarm.detach()

    @time_critical
    def test_session_context(self):
        delay = .001
        iters = 32

        with Swarm(delay=delay, headers=[{}] * 4) as swarm:
            t_start = time()

            for i in range(iters):
                with swarm.session():
                    pass

            t_total = time() - t_start

            mean_duration = (t_total / iters) * len(swarm)

            # The above formula is correct only if iters is a multiple of swarm size or infinite
            self.assertEqual(0, iters % len(swarm))

            # ensure delay is hard lower limit
            self.assertLess(delay, mean_duration)

            # tolerance of 25%
            self.assertTrue(isclose(delay, mean_duration, rel_tol=25e-2))

        Swarm.detach()

        with Swarm(delay=delay, headers=[{}]) as swarm:
            with swarm.session():
                with self.assertRaises(Empty):
                    with swarm.session(1e-16):
                        pass

    def test_on_init(self):
        sids = set()

        def init_callback(session):
            sids.add(session.id)

        with Swarm(on_init=init_callback, headers=[{}] * 3):
            pass

        self.assertEqual(3, len(sids))

    def test_on_close(self):
        sids = set()

        def close_callback(session):
            sids.add(session.id)

        with Swarm(on_close=close_callback, headers=[{}] * 3):
            pass

        self.assertEqual(3, len(sids))

    def test_open_close(self):
        swarm = Swarm(headers=[{}] * 3)

        self.assertEqual(0, len(swarm))
        with self.assertRaises(MosquitoError):
            with swarm.session():
                pass

        swarm.open()
        with swarm.session():
            pass

        self.assertEqual(3, len(swarm))

        swarm.close()

        self.assertEqual(0, len(swarm))
        with self.assertRaises(MosquitoError):
            with swarm.session():
                pass

        with swarm:
            self.assertEqual(3, len(swarm))
            with swarm.session():
                pass

        self.assertEqual(0, len(swarm))

        with Swarm() as swarm:
            self.assertEqual(3, len(swarm))
