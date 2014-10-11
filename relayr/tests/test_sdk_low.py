#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module contains tests of the lower level of the Relayr API Python client.

Configuration data like user email address or anything like that comes from 
a config.py file. The values there need to be set propperly before running
theses tests!
"""

import sys
import time
import json
import unittest
if sys.version_info[:2] < (2, 7):
    import unittest2 as unittest

from relayr import core, exceptions

import config


TIMEOUT = 2
PY_VERSION = sys.version_info[0]


class CompatibilityTestCase(unittest.TestCase):
    "Tests for compatibility issues."

    def setUp(self):
        if PY_VERSION == 2:
            self.assertRaisesRegex = self.assertRaisesRegexp

    def test_get_resource_missing_credentials(self):
        """
        Test getting a resource without the necessary credentials.
        """

        # curl https://api.relayr.io/devices/<deviceID>

        context = config.testset1
        deviceID = context['deviceID']
        details = 'The supplied authentication is not authorized to access this resource.'

        # deviceID = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
        # details = 'URL could not be routed.'

        exc = exceptions.RelayrApiException
        self.assertRaisesRegex(exc, details, core.device, deviceID)


class DeviceTestCase(unittest.TestCase):
    "Tests on devices."

    maxDiff = None
    
    def test_device_get_info(self):
        """
        Test getting info for some device.
        """

        context = config.testset1
        t0 = time.time()
        res = core.device(context['deviceID'], token=context['token'])
        t = time.time() - t0

        exp = {
            "name": "My Wunderbar Thermometer & Humidity Sensor", 
            "public": True, 
            "secret": "474297", 
            "owner": "297a005c-f11e-4b2a-92d0-1d42fa4400b6", 
            "model": {
                "readings": [
                    {
                        "meaning": "temperature", 
                        "minimum": -100.0, 
                        "maximum": 100.0, 
                        "unit": "celsius", 
                        "precision": 0.25
                    }, 
                    {
                        "meaning": "humidity", 
                        "unit": "percent"
                    }
                ], 
                "manufacturer": "Relayr GmbH", 
                "id": "ecf6cf94-cb07-43ac-a85e-dccf26b48c86", 
                "name": "Wunderbar Thermometer & Humidity Sensor"
            }, 
            "id": "48c82865-a1c8-4cd7-b8be-534f3f638e2b", 
            "firmwareVersion": "1.0.0"
        }

        self.assertEqual(res.keys(), exp.keys())
        for k in res.keys():
            self.assertEqual(res[k], exp[k])            
        self.assertTrue(t <= TIMEOUT)


class AppTestCase(unittest.TestCase):
    "Tests on apps that do require authentication."

    maxDiff = None
    
    def test_app_update_info(self):
        """
        Test updating info for some app.
        """

        context = config.testset1

        t0 = time.time()
        res = core.app_patch(context['appID'], redirectUri=context['redirectURI'],
            relayrAPI=context['relayrAPI'], token=context['token'])
        t = time.time() - t0
        
        exp = {
            "id": context['appID'],
            "name": context['appName'],
            "publisher": context['publisherID'],
            "clientId": context['clientId'],
            "clientSecret": context['clientSecret'],
            "description": context['description'],
            "redirectUri": context['redirectURI']
        }
        self.assertEqual(json.dumps(res), json.dumps(exp))
        self.assertTrue(t <= TIMEOUT)


class UserTestCase(unittest.TestCase):
    "Tests on users that do require authentication."

    def test_get_user_info(self):
        """
        Test getting info for currently authenticated user.
        """

        context = config.testset1
        t0 = time.time()
        res = core.user_info(**context)
        t = time.time() - t0
        
        exp = {
            "email": context['userEmail'], 
            "id": context['userID'], 
            "name": context['userName']
        }
        self.assertEqual(res, exp)
        self.assertTrue(t <= TIMEOUT)


    @unittest.skip('not working, yet')
    def test_user_wunderbar(self):
        """
        Test return the IDs and Secrets of the Master Module and Sensor Modules.
        """
        
        context = config.testset1
        t0 = time.time()
        res = core.user_wunderbar(context['userID'])
        t = time.time() - t0
        
        exp = {
        }
        # self.assertEqual(json.dumps(res), json.dumps(exp)) # .json()?
        # self.assertTrue(t <= TIMEOUT)


    @unittest.skip('not working, yet')
    def test_user_update_info(self):
        """
        Test updating info for currently authenticated user.
        """

        context = config.testset1
        
        t0 = time.time()
        res = core.user_update_info(context['userID'], name='somename')
        t = time.time() - t0

        exp = {
            "email": context['userEmail'], 
            "id": context['userID'], 
            "name": "somename"
        }
        self.assertEqual(res, exp)
        self.assertTrue(t <= TIMEOUT)


    def test_register_wunderbar(self):
        """
        Test register a Wunderbar.
        """

        context = config.testset1
        res = core.user_wunderbar(**context)
        
        self.assertTrue(len(res) == 7) # 1 master + 6 sensors
        expected_keys = ['masterModule', 'infrared', 'gyroscope', 'light', 
            'thermometer', 'microphone', 'bridge']
        self.assertTrue(set(expected_keys).issubset(set(res.keys())))


    @unittest.skip('not yet tested')
    def test_remove_wunderbar(self):
        """
        Test remove a Wunderbar.
        """

        # Be sure the code below doesn't get run.
        return
        
        context = config.testset1
        res = core.user_wunderbar_remove_all(**context)


class PublicTestCase(unittest.TestCase):
    "Tests accessing public info that do not require any credentials."

    def test_validate_existing_email_address(self):
        """
        Test validating an existing user email address.
        """

        context = config.testset1
        t0 = time.time()
        res = core.validate_email(context['userEmail'])
        t = time.time() - t0

        self.assertEqual(res['exists'], True)
        self.assertTrue(t <= TIMEOUT)


    def test_validate_nonexisting_email_address(self):
        """
        Test validating an non existing (hopefully) user email address.
        """

        t0 = time.time()
        res = core.validate_email('god@in.heaven')
        t = time.time() - t0

        self.assertEqual(res['exists'], False)
        self.assertTrue(t <= TIMEOUT)


    def test_list_all_publishers(self):
        """
        Test listing all publishers.
        """

        t0 = time.time()
        publishers = core.list_all_publishers()
        t = time.time() - t0

        self.assertEqual(type(publishers), list)
        expected_keys = set(['id', 'name', 'owner'])
        for p in publishers:
            self.assertEqual(set(p.keys()), expected_keys)


    def test_list_all_apps(self):
        """
        Test listing all apps.
        """

        t0 = time.time()
        apps = core.list_all_apps()
        t = time.time() - t0

        self.assertEqual(type(apps), list)
        expected_keys = set(['id', 'name']) # 'description' not always present
        for a in apps:
            self.assertTrue(expected_keys.issubset(set(a.keys())))
                

    def test_list_all_public_devices(self):
        """
        Test listing all public devices.
        """

        t0 = time.time()
        devices = core.list_all_public_devices()
        t = time.time() - t0

        self.assertEqual(type(devices), list)
        expected_keys = set(['model', 'firmwareVersion', 'id', 'name'])
        for d in devices:
            self.assertEqual(set(d.keys()), expected_keys)


    def test_list_all_device_models(self):
        """
        Test listing all device models.
        """

        t0 = time.time()
        models = core.list_all_device_models()
        t = time.time() - t0

        self.assertEqual(type(models), list)
        expected_keys = set(['id', 'readings', 'firmwareVersions',
                'manufacturer', 'name'])
        for m in models:
            self.assertEqual(set(m.keys()), expected_keys)


    def test_list_all_device_models_meanings(self):
        """
        Test listing all device model meanings.
        """

        t0 = time.time()
        models = core.list_all_device_model_meanings()
        t = time.time() - t0

        self.assertEqual(type(models), list)
        expected_keys = set(['key', 'value'])
        for m in models:
            self.assertEqual(set(m.keys()), expected_keys)


class ServerTestCase(unittest.TestCase):
    "Tests on server/cloud..."

    def test_get_user_info(self):
        """
        Test retrieve the token representing a dev. and a specific Relayr app.
        """

        from config import testset1 as context
        appID = context['appID']
        # del context['appID']
        t0 = time.time()

        # res = core.server_token(appID, **context)
        res = core.server_token(appID, relayrAPI=context['relayrAPI'],
                token=context['token'])
        t = time.time() - t0

        self.assertTrue('token' in res and 'expiryDate' in res)
        self.assertTrue(t <= TIMEOUT)


if __name__ == "__main__":
    unittest.main()
