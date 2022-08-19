#!/usr/bin/env python3
# Standard library modules.
import os
from unittest import TestLoader, TextTestRunner

# Third party modules.

# Local modules
from mosquito.tests import httpbin

# Globals and constants variables.


def mosquito_test():
    path = os.path.dirname(__file__)

    print(f'Use httpbin instance on {httpbin()} for testing.')
    print(f'Run unit tests in: {path}\n')

    loader = TestLoader()
    suite = loader.discover(start_dir=path)
    runner = TextTestRunner()

    runner.run(suite)


if __name__ == '__main__':
    mosquito_test()
