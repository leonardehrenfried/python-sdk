# -*- coding: utf-8 -*-

"""
This module contains tests of the Relayr restful HTTP API client.

The tests are written in plain Python code, without using the unittest frame-
work, so you can run them via py.test (an alternative to unittest! As the
functions are also mostly fully self-contained you can copy/paste/run individual
test method bodies in an interactive Python session! And where the test methods
rely on some fixture parameter the values they provide can be often easily
replaced in copied code.

By convention, test fixtures are Python files with a ``fixture_`` prefix and
provide values used inside the tests like e.g. a user email address or access
token. The fixture loaders are contained in ``conftest.py`` where they will be
discovered by pytest.

Attention: The values in these fixture files need to be set properly before
running the tests!
"""

import pytest


class TestInstallation(object):
    "Test installation aspects."

    def test_imports(self):
        "Test importing various bits."
        from relayr.version import __version__
        from relayr import Client
        from relayr.resources import User, Publisher, App, Transmitter, \
            Device, DeviceModel
        from relayr.exceptions import RelayrApiException
        from relayr.api import perform_request


class TestRawAPI(object):
    "Test raw HTTP access to some API endpoints."

    def test_raw_server_status(self, fix_anonymous):
        "Test server status."
        from requests import get
        relayrAPI = fix_anonymous.testset0['relayrAPI']
        resp = get('%s/server-status' % relayrAPI)
        assert resp.json() == {'database': 'ok'}

    def test_raw_non_existing_endpoint(self, fix_anonymous):
        "Test accessing a non-existing API endpoint."
        from requests import get
        relayrAPI = fix_anonymous.testset0['relayrAPI']
        resp = get('%s/this-should-not-exist' % relayrAPI)
        assert resp.status_code == 404

    def test_raw_all_publishers(self, fix_anonymous):
        "Test accessing list of all public publishers."
        # More or less the same for othere resources like devices, etc. 
        # with partly different expected keys:
        #   /device-models/meanings: key, value
        #   /device-models: id, readings, firmwareVersions, manufacturer, name
        #   /devices/public: model, firmwareVersion, id, name 
        #   /apps: id, name 
        from requests import get
        relayrAPI = fix_anonymous.testset0['relayrAPI']
        resp = get('%s/publishers' % relayrAPI)
        assert resp.status_code == 200
        publishers = resp.json()
        assert type(publishers) == list
        expected_keys = set(['id', 'name', 'owner'])
        for p in publishers:
            assert expected_keys.issubset(set(p.keys())) == True


class TestRequests(object):
    "Test performing requests."

    def test_unknown_endpoint(self, fix_anonymous):
        "Test accessing an unknown API endpoint."
        from relayr.api import perform_request
        from relayr.exceptions import RelayrApiException
        with pytest.raises(RelayrApiException) as excinfo:
            url = '%s/this-should-not-exist' % fix_anonymous.testset0['relayrAPI']
            resp = perform_request('GET', url)
        assert str(excinfo.value).startswith('URL could not be routed.')

    def test_unknown_endpoint_data(self, fix_anonymous):
        "Test accessing an unknown API endpoint with body data."
        from relayr.api import perform_request
        from relayr.exceptions import RelayrApiException
        with pytest.raises(RelayrApiException) as excinfo:
            url = '%s/this-should-not-exist' % fix_anonymous.testset0['relayrAPI']
            resp = perform_request('POST', url, data={'foo': 42, 'bar': 23})
        assert str(excinfo.value).startswith('URL could not be routed.')
        assert '--data "foo=42&bar=23"' in str(excinfo.value) or \
            '--data "bar=23&foo=42"' in str(excinfo.value)


class TestAPIAnonymous(object):
    "Test low-level access to API endpoints without a need for credentials."

    def test_server_status(self):
        "Test server status."
        from relayr import Client
        assert Client().api.get_server_status() == {u'database': u'ok'}

    def test_users_validate_non_existing(self, fix_anonymous):
        "Test validate non-existing user email."
        from relayr import Client
        userName = fix_anonymous.testset0['userEmail']
        assert Client().api.get_users_validate(userName) == {u'exists': False}

    def test_exception_missing_creds(self):
        "Test raising exception for missing credentials."
        from relayr import Client
        from relayr.exceptions import RelayrApiException
        with pytest.raises(RelayrApiException) as excinfo:
            info = Client().api.get_oauth2_user_info()
        assert str(excinfo.value).startswith('CredentialsMissing')

    def test_list_all_publishers(self):
        pass
