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


class TestDeviceBookmarks(object):
    "Test device bookmarks."

    def test_get_user_bookmarked_devices(self, fix_registered):
        "Test get user's bookmarked devices."
        from relayr import Client
        token = fix_registered.testset1['token']
        c = Client(token=token)
        user = c.get_user()
        b_devs = user.get_bookmarked_devices()
        assert type(list(b_devs)) == list

    def test_post_user_devices_bookmarks(self, fix_registered):
        "Test get user's bookmarked devices."
        from relayr import Client
        token = fix_registered.testset1['token']
        c = Client(token=token)
        user = c.get_user()


class TestAPI(object):
    "Test low-level access to API endpoints."

    def test_validate_registered_user(self, fix_registered):
        "Test validate an existing user email address."
        from requests import get
        context = fix_registered.testset1
        url = '{relayrAPI}/users/validate?email={userEmail}'.format(**context)
        resp = get(url)
        assert resp.status_code == 200
        j = resp.json()
        assert resp.json()['exists'] == True

    def test_get_appdev_token(self, fix_registered):
        "Test get appdev token."
        from relayr import Client
        token = fix_registered.testset1['token']
        c = Client(token=token)
        app = c.get_app()
        res = c.api.get_oauth2_appdev_token(app.id)
        assert res['token'] == token

    @pytest.mark.skip(reason="unfinished") ###################
    def test_post_oauth2_token(self, fix_registered):
        "Test post oauth2 token."
        from relayr import Client
        token = fix_registered.testset1['token']
        c = Client(token=token)
        # res = c.api.post_oauth2_token('clientID', 'clientSecret', 'code', 'redirectURI')

    def test_connected_user(self, fix_registered):
        "Test get info about the currently connected user."
        from relayr import Client
        token = fix_registered.testset1['token']
        c = Client(token=token)
        info = c.api.get_oauth2_user_info()
        for key in 'name email id'.split():
            assert key in info

    def test_connected_app(self, fix_registered):
        "Test get info about the currently connected app."
        from relayr import Client
        token = fix_registered.testset1['token']
        c = Client(token=token)
        info = c.api.get_oauth2_app_info()
        for key in 'name description id'.split():
            assert key in info

    def test1_get_token(self, fix_registered):
        "Test get current token and compare with the one given to connect."
        from relayr import Client
        token = fix_registered.testset1['token']
        c = Client(token=token)
        app_id = c.api.get_oauth2_app_info()['id']
        info = c.api.get_oauth2_appdev_token(app_id)
        for key in 'token expiryDate'.split():
            assert key in info
        assert token == info['token']

    def _test_update_user(self, fix_registered):
        "Test update user attribute, here: name."
        from relayr import Client
        ## TODO: check if a regular user can change his own attributes...
        token = fix_registered.testset1['token']
        c = Client(token=token)
        info = c.api.get_oauth2_user_info()
        c.api.patch_user(info['id'], name='dcg')

    def test_get_transmitters(self, fix_registered):
        "Test get user's transmitters."
        from relayr import Client
        token = fix_registered.testset1['token']
        c = Client(token=token)
        user_info = c.api.get_oauth2_user_info()
        trans_info = c.api.get_user_transmitters(user_info['id'])
        for trans in trans_info:
            for key in 'owner name id'.split(): # plus others...
                assert key in trans

    def test_apps_of_connected_user(self, fix_registered):
        "Get apps of connected user."
        from relayr import Client
        token = fix_registered.testset1['token']
        c = Client(token=token)
        apps = c.api.get_user_apps(c.api.get_oauth2_user_info()['id'])
        assert len(apps) > 0
        assert type(apps[0]) == dict

    def test_device_credentials(self, fix_registered):
        "Test get credentials for subscribing to a device."
        from relayr import Client
        token = fix_registered.testset1['token']
        c = Client(token=token)
        deviceID = fix_registered.testset1['deviceID']
        creds = c.api.post_devices_supscription(deviceID)
        for key in 'authKey subscribeKey cipherKey channel'.split():
            assert key in creds

    def test_get_wunderbar(self, fix_registered):
        "Test get info about the user's registered wunderbar device."
        from relayr import Client
        token = fix_registered.testset1['token']
        c = Client(token=token)
        user_info = c.api.get_oauth2_user_info()
        wb_dev_info = c.api.post_user_wunderbar(user_info['id'])
        assert len(wb_dev_info) == 7 # 6 sensors plus one transmitter
        owner_ids = [dev['owner'] for dev in wb_dev_info.values()]
        assert len(set(owner_ids)) == 1
        assert user_info['id'] == owner_ids[0]
        for typ, info in wb_dev_info.items():
            for key in 'owner name id'.split(): # plus others...
                assert key in info


class TestClient(object):
    "Test high-level access via API client."

    def test_public_resources(self, fix_registered):
        "Get public resources."
        from relayr import Client
        from relayr.resources import App, Publisher, Device, DeviceModel
        token = fix_registered.testset1['token']
        c = Client(token=token)
        assert next(c.get_public_apps()).__class__ == App
        assert next(c.get_public_devices()).__class__ == Device
        assert next(c.get_public_device_models()).__class__ == DeviceModel
        assert next(c.get_public_publishers()).__class__ == Publisher

    def test_users_resources(self, fix_registered):
        "Test get user's resources."
        from relayr import Client
        from relayr.resources import User, Publisher, App, Device
        token = fix_registered.testset1['token']
        c = Client(token=token)
        usr = c.get_user()
        assert usr.__class__ == User
        assert c.get_app().__class__ == App
        assert next(usr.get_apps()).__class__ == App
        assert next(usr.get_devices()).__class__ == Device
        assert next(usr.get_publishers()).__class__ == Publisher

    def test_user_name(self, fix_registered):
        "Test get name attribute of User object for connected user."
        from relayr import Client
        token = fix_registered.testset1['token']
        c = Client(token=token)
        usr = c.get_user()
        assert usr.name == fix_registered.testset1['userName']

    def test4(self, fix_registered):
        "Test get publishers for connected user."
        from relayr import Client
        token = fix_registered.testset1['token']
        c = Client(token=token)
        usr = c.get_user()
        # pubs = list(usr.get_publishers()) # The supplied authentication is not authorized to access this resource.

    def test_access_device(self, fix_registered):
        "Test access a public device."
        from relayr import Client
        from relayr.resources import Device
        token = fix_registered.testset1['token']
        deviceID = fix_registered.testset1['deviceID']
        c = Client(token=token)
        dev = Device(id=deviceID)

    def test_send_command_device(self, fix_registered):
        "Test send a command to a device."
        from relayr import Client
        from relayr.resources import Device
        token = fix_registered.testset1['token']
        c = Client(token=token)
        deviceID = fix_registered.testset1['deviceID']
        dev = Device(id=deviceID, client=c)
        dev.get_info()
        dev.send_command('led', {'cmd': 1})
        # Eye-ball test, since reading the LED status is not yet implemented
        # in the firmware.

    # @pytest.xfail("no api method?")
    def test_publish_device(self):
        "Test make a device public/private."

    def test_get_wunderbar_devices(self, fix_registered):
        "Test get user's registered wunderbar devices and master."
        from relayr import Client
        token = fix_registered.testset1['token']
        c = Client(token=token)
        usr = c.get_user()
        items = list(usr.register_wunderbar())
        assert len(items) == 7


class TestTransmitters(object):
    "Tests on transmitters."

    def test_get_transmitter_devices(self, fix_registered):
        "Test getting devices of a known transmitter."
        from relayr import Client
        from relayr.resources import Transmitter
        token = fix_registered.testset1['token']
        transmitterID = fix_registered.testset1['transmitterID']
        c = Client(token=token)
        t = Transmitter(id=transmitterID, client=c)
        t.get_info()
        assert t.name == fix_registered.testset1['transmitterName']
        devs = t.get_connected_devices()
        assert len(list(devs)) == 6


class TestApps(object):
    "Tests on apps."

    def test_app_info(self, fix_registered):
        "Test getting info for the app."
        from relayr import Client
        token = fix_registered.testset1['token']
        c = Client(token=token)
        app = c.get_app()
        assert hasattr(app, 'id')

    def test_app_update(self, fix_registered):
        "Test update info for some app."
        # This is actually done twice for making this an idempotent operation.
        from relayr import Client
        token = fix_registered.testset1['token']
        c = Client(token=token)
        app = c.get_app()
        initial_app_name = app.name
        # update name to something silly
        silly_name = 'HolyWhat?'
        app.update(name=silly_name)
        assert app.name == silly_name
        # update name to previous name
        app.update(name=initial_app_name)        
        assert app.name == initial_app_name


class TestWunderbar(object):
    "Tests accessing a wunderbar."

    def test_find_wunderbar_devices(self, fix_registered):
        "Test get all devices on a Wunderbar."
        from relayr import Client
        from relayr.resources import Device, Transmitter
        token = fix_registered.testset1['token']
        c = Client(token=token)
        usr = c.get_user()
        assert usr.name == fix_registered.testset1['userName']
        devs = usr.register_wunderbar()
        for d in devs:
            assert d.__class__ in (Device, Transmitter)
            assert hasattr(d, 'id')


class TestPublishers(object):
    "Tests on publishers."

    def test_pub_get_apps(self, fix_registered):
        "Test getting apps for some publisher."
        from relayr import Client
        from relayr.resources import Publisher
        publisherID = fix_registered.testset1['publisherID']
        pub = Publisher(id=publisherID, client=Client())
        apps = pub.get_apps()
        assert len(apps) >= 1
        assert 'id' in apps[0]

    def test_pub_get_apps_extended(self, fix_registered):
        "Test getting extended apps for some publisher."
        from relayr import Client
        from relayr.resources import Publisher
        publisherID = fix_registered.testset1['publisherID']
        pub = Publisher(id=publisherID, client=Client())
        apps = pub.get_apps(extended=True)
        assert len(apps) >= 1
        assert 'clientId' in apps[0]
