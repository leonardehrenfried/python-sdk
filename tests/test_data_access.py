# -*- coding: utf-8 -*-

"""
This module contains tests of the Relayr restful HTTP API client.

Attention: The values in these fixture files need to be set properly before
running the tests!
"""

import pytest


class TestPubNub(object):
    "Test accessing device data via a PubNub connection."

    def receive(self, message, channel):
        "Callback method for data connection."
        print(message) # suppressed by py.test
        self.received_data.append(message)

    def test_read_pubnub_device_10s(self, fix_registered):
        "Test connect to a device via PubNub and read data for some time."
        import time
        from relayr import Client
        from relayr.resources import Device
        token = fix_registered.testset1['token']
        deviceID = fix_registered.testset1['deviceID']
        self.received_data = []
        c = Client(token=token)
        dev = Device(id=deviceID, client=c).get_info()
        usr = c.get_user()
        app = c.get_app()
        conn = usr.connect_device(app, dev, self.receive)
        conn.start()
        time.sleep(10)
        conn.stop()
        assert len(self.received_data) > 0
        for item in self.received_data:
            assert 'ts' in item
