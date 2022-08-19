# Standard library modules.
from unittest import TestCase

# Third party modules.

# Local modules
from mosquito import MosquitoError
from mosquito.api import registry, register_attributes, attribute, swarm
from mosquito.tests.utils import httpbin

# Globals and constants variables.


class TestFunctions(TestCase):
    def setUp(self):
        self.attribute_registry_backup = dict(registry())

    def tearDown(self):
        registry().clear()
        registry().update(self.attribute_registry_backup)

    def test_register_attributes(self):
        register_attributes(headers=[42])
        self.assertEqual([42], registry().get('headers'))

        with self.assertRaises(AttributeError):
            register_attributes(fnord=[])

    def test_attribute(self):
        attribute('headers')([42])
        self.assertEqual([42], registry().get('headers'))

        with self.assertRaises(AttributeError):
            attribute('fnord')([])

    def test_swarm(self):
        user_agents = {'foo', 'bar', 'baz'}
        register_attributes(headers=[{'user-agent': ua} for ua in user_agents])

        with swarm(max_attempts=2, repeat_on=(503,)) as scheduler:
            self.assertEqual(3, len(scheduler.swarm))

            uas = set()
            for _ in range(len(user_agents)):
                response = scheduler.get(httpbin('/user-agent'))
                uas.add(response.json().get('user-agent'))

            self.assertEqual(user_agents, uas)

            with self.assertRaises(MosquitoError):
                _ = scheduler.get(httpbin('/status/503'))
