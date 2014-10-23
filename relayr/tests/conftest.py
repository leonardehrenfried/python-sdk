"""
This module contains test fixture loaders that py.test will find here when
executing test cases.
"""

import os
import sys

import pytest


@pytest.fixture()
def anonymous_user():
    "A test fixture for an anonymous user."
    env = {
        'userEmail': 'god@in.heaven',
        'result': '42'
    }
    return env

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
