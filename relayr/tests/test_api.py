#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module contains some tests of the plain Relayr restful HTTP API.

Configuration data like user email address or anything like that comes from 
a config.py file. The values there need to be set propperly before running
theses tests! 

This test file can be run entirely without the Relayr Python client. It is 
only meant to test some API endpoints "on the (HTTP) wire", so there is 
no intent to make this much more complete. In addition the response time is
measured and tested for some given timeout value specified in this module.
"""

import sys
import time
import unittest
if sys.version_info[:2] < (2, 7):
    import unittest2 as unittest

from jinja2 import Template
import requests

import config


TIMEOUT = 0.75


class PublicTestCase(unittest.TestCase):
    """
    A collection of tests for public endpoints which don't need any credentials.
    """
    
    def test_validate_existing_email_address(self):
        """
        Test validate an existing user email address.
        """

        context = config.testset1
        template = Template('{{relayrAPI}}/users/validate?email={{userEmail}}')
        url = template.render(context)
        t0 = time.time()
        resp = requests.get(url)
        resp.connection.close()
        t = time.time() - t0

        self.assertEqual(resp.status_code, 200)

        j = resp.json()
        self.assertEqual(j['exists'], True)
        self.assertTrue(t <= TIMEOUT)


    def test_validate_not_existing_email_address(self):
        """
        Test validate a not existing user email address.
        """

        context = config.testset0
        template = Template('{{relayrAPI}}/users/validate?email={{userEmail}}')
        url = template.render(context)
        t0 = time.time()
        resp = requests.get(url)
        resp.connection.close()
        t = time.time() - t0

        self.assertEqual(resp.status_code, 200)

        j = resp.json()
        self.assertEqual(j['exists'], False)
        self.assertTrue(t <= TIMEOUT)


    def test_list_all_publishers(self):
        """
        Test listing all publishers.
        """

        context = config.testset1
        template = Template('{{relayrAPI}}/publishers')
        url = template.render(context)
        t0 = time.time()
        resp = requests.get(url)
        resp.connection.close()
        t = time.time() - t0

        self.assertEqual(resp.status_code, 200)

        publishers = resp.json()
        self.assertEqual(type(publishers), list)
        expected_keys = set(['id', 'name', 'owner'])
        for p in publishers:
            self.assertTrue(expected_keys.issubset(set(p.keys())))


    def test_list_all_apps(self):
        """
        Test listing all apps.
        """

        context = config.testset1
        template = Template('{{relayrAPI}}/apps')
        url = template.render(context)
        t0 = time.time()
        resp = requests.get(url)
        resp.connection.close()
        t = time.time() - t0

        self.assertEqual(resp.status_code, 200)

        apps = resp.json()
        self.assertEqual(type(apps), list)
        expected_keys = set(['id', 'name']) # 'description' not always present
        for a in apps:
            self.assertTrue(expected_keys.issubset(set(a.keys())))


    def test_list_all_public_devices(self):
        """
        Test listing all public devices.
        """

        context = config.testset1
        template = Template('{{relayrAPI}}/devices/public') # ?meaning=meaning
        url = template.render(context)
        t0 = time.time()
        resp = requests.get(url)
        resp.connection.close()
        t = time.time() - t0

        self.assertEqual(resp.status_code, 200)

        devices = resp.json()
        self.assertEqual(type(devices), list)
        expected_keys = set(['model', 'firmwareVersion', 'id', 'name'])
        for d in devices:
            self.assertTrue(expected_keys.issubset(set(d.keys())))


    def test_list_all_device_models(self):
        """
        Test listing all available device models.
        """

        context = config.testset1
        template = Template('{{relayrAPI}}/device-models')
        url = template.render(context)
        t0 = time.time()
        resp = requests.get(url)
        resp.connection.close()
        t = time.time() - t0

        self.assertEqual(resp.status_code, 200)

        models = resp.json()
        self.assertEqual(type(models), list)
        expected_keys = set(['id', 'readings', 'firmwareVersions',
            'manufacturer', 'name'])
        for m in models:
            self.assertTrue(expected_keys.issubset(set(m.keys())))


    def test_list_all_device_model_meanings(self):
        """
        Test listing all available device model meanings.
        """

        context = config.testset1
        template = Template('{{relayrAPI}}/device-models/meanings')
        url = template.render(context)
        t0 = time.time()
        resp = requests.get(url)
        resp.connection.close()
        t = time.time() - t0

        self.assertEqual(resp.status_code, 200)

        meanings = resp.json()
        self.assertEqual(type(meanings), list)
        expected_keys = set(['key', 'value'])
        for m in meanings:
            self.assertTrue(expected_keys.issubset(set(m.keys())))


if __name__ == "__main__":
    unittest.main()
