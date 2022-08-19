# Standard library modules.
from queue import Empty
from unittest import TestCase

# Third party modules.

# Local modules
from mosquito import MosquitoError, Swarm, Scheduler
from mosquito.tests.utils import httpbin

# Globals and constants variables.


class TestScheduler(TestCase):
    def setUp(self):
        Swarm.detach()

        self.swarm = Swarm()
        self.swarm.open()

        self.scheduler = Scheduler(self.swarm)

    def tearDown(self):
        self.swarm.close()

    def test__request(self):
        with self.assertRaises(MosquitoError):
            self.scheduler.get(httpbin('/status/404'))

        scheduler = Scheduler(self.swarm, repeat_on=(503,))
        try:
            scheduler.get(httpbin('/status/503'))
        except MosquitoError as me:
            self.assertIn('1', str(me))

        scheduler = Scheduler(self.swarm, max_attempts=3, repeat_on=(503,))
        try:
            scheduler.get(httpbin('/status/503'))
        except MosquitoError as me:
            self.assertIn('3', str(me))

        with self.assertRaises(AssertionError):
            _ = Scheduler(self.swarm, max_attempts=0)

        with self.assertRaises(AssertionError):
            _ = Scheduler(self.swarm, repeat_on=(200,))

    def test_get(self):
        response = self.scheduler.get(httpbin('/get'))
        self.assertEqual('GET', response.request.method)

    def test_options(self):
        response = self.scheduler.options(httpbin('/get'))
        self.assertEqual('OPTIONS', response.request.method)

    def test_head(self):
        response = self.scheduler.head(httpbin('/get'))
        self.assertEqual('HEAD', response.request.method)

    def test_post(self):
        response = self.scheduler.post(httpbin('/post'))
        self.assertEqual('POST', response.request.method)

    def test_put(self):
        response = self.scheduler.put(httpbin('/put'))
        self.assertEqual('PUT', response.request.method)

    def test_patch(self):
        response = self.scheduler.patch(httpbin('/patch'))
        self.assertEqual('PATCH', response.request.method)

    def test_delete(self):
        response = self.scheduler.delete(httpbin('/delete'))
        self.assertEqual('DELETE', response.request.method)

    def test_timeout(self):
        scheduler =  Scheduler(self.swarm, session_timeout=1e-16)
        with scheduler.swarm.session():
            with self.assertRaises(Empty):
                scheduler.get(httpbin('/get'))
