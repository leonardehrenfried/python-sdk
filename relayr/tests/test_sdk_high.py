#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module contains tests of the higher level of the Relayr API Python client.

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

from relayr import exceptions
from relayr.apps import App
from relayr.publishers import Publisher
from relayr.users import User
import config

PY_VERSION = sys.version_info[0]


class AppTestCase(unittest.TestCase):
    "Tests on apps."

    maxDiff = None
    
    def test_app_get_info(self):
        """
        Test getting info for some app.
        """

        from config import testset1 as context
        app = App(context['appID'])
        res = app.get_info()
        
        self.assertTrue('id' in res)        
        self.assertTrue(res['id'] in context['appID'])        


    def test_app_update_info(self):
        """
        Test updating info for some app.
        
        This is actually done twice for making this an idempotent operation.
        """

        from config import testset1 as context
        app = App(context['appID'])
        initial_app_name = app.get_info()['name']

        # update name to something silly
        silly_name = 'HolyWhat?'
        res = app.update(name=silly_name, token=context['token'])
        self.assertTrue(res['name'] == silly_name)        

        # update name to previous name
        res = app.update(name=initial_app_name, token=context['token'])        
        self.assertTrue(res['name'] == initial_app_name)        


class PublisherTestCase(unittest.TestCase):
    "Tests on publishers."

    maxDiff = None
    
    def test_pub_get_apps(self):
        """
        Test getting apps for some publisher.
        """

        context = config.testset2
        pub = Publisher(context['publisherID'])
        apps = pub.get_apps()

        self.assertTrue(len(apps) >= 2)        
        self.assertTrue('id' in apps[0])        


    def test_pub_get_apps_extended(self):
        """
        Test getting extended apps for some publisher.
        """

        context = config.testset2
        pub = Publisher(context['publisherID'])
        apps = pub.get_apps(extended=True)

        self.assertTrue(len(apps) >= 2)        
        self.assertTrue('id' in apps[0])        


class UserTestCase(unittest.TestCase):
    "Tests on users."

    maxDiff = None
    
    @unittest.skip('not tested now')
    def _test_register_wunderbar(self):
        """
        Test registering a Wunderbar.
        """

        # works
        context = config.testset1
        usr = User(**context)
        res = usr.register_wunderbar()
        
        self.assertTrue(len(res) == 7) # 1 master + 6 sensors
        expected_keys = ['masterModule', 'infrared', 'gyroscope', 'light', 
            'thermometer', 'microphone', 'bridge']
        self.assertTrue(set(expected_keys).issubset(set(res.keys())))


    @unittest.skip('not yet tested')
    def test_remove_wunderbar(self):
        """
        Test removing a Wunderbar.
        """

        # Be sure the code below doesn't get run.
        return
        
        context = config.testset1
        usr = User(**context)
        res = usr.remove_wunderbar()


if __name__ == "__main__":
    unittest.main()
