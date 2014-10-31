"""
This module contains test fixture loaders that py.test will find here when
executing test cases.
"""

import os
import sys

import pytest


## TODO: maybe use importlib.import_module

@pytest.fixture(scope='module')
def fix_anonymous():
    "Return fixture for anonymous API access."
    sys.path.insert(0, os.path.dirname(__file__))
    import fixture_anonymous
    del sys.path[0]
    return fixture_anonymous

@pytest.fixture(scope='module')
def fix_registered():
    "Return fixture for access by a registered user."
    sys.path.insert(0, os.path.dirname(__file__))
    import fixture_registered
    del sys.path[0]
    return fixture_registered
