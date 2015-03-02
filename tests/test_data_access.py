# -*- coding: utf-8 -*-

"""
This module contains tests of the Relayr restful HTTP API client.

Attention: The values in these fixture files need to be set properly before
running the tests!

Some of these tests write on stdout which gets suppressed by py.test,
unless it is called on the command-line with the '-s' option. Some
need to be stopped with CTRL-C, and are skipped here, but can be run
individually when removing the skipping decorator.
"""

import ssl
import platform

import pytest

from relayr.compat import PY26


class TestPubNub(object):
    "Test accessing device data via a PubNub connection."

    def receive(self, message, channel):
        "Callback method for data connection."
        print(message) # suppressed by py.test, unless called with -s
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


class TestMqttChannelCreds(object):
    "Test creating MQTT channel credentials."

    def test_repeated_creation(self, fix_registered):
        "Test repeatedly creating channel credentials."
        from relayr import Api
        import paho.mqtt.client as mqtt
        token = fix_registered.testset1['token']
        api = Api(token=token)
        deviceId = fix_registered.testset1['deviceID']

        # test clientIds are different
        creds_1 = api.post_channel(deviceId, 'mqtt')
        creds_2 = api.post_channel(deviceId, 'mqtt')
        assert creds_1['credentials']['clientId'] != creds_2['credentials']['clientId']

        # test the rest is the same
        del creds_1['credentials']['clientId']
        del creds_2['credentials']['clientId']
        assert creds_1 == creds_2

        # cleanup, removing created stuff
        channelId = creds_1['channelId']
        api.delete_channel_id(channelId)
        channels = api.get_device_channels(deviceId)['channels']
        channelIds = [ch['channelId'] for ch in channels]
        assert channelId not in channelIds


@pytest.mark.skipif(PY26==True, reason="Python 2.7 is the minimum supported version for TLS.")
class TestMqttStreamsShort(object):
    "Test accessing device data via a single topic MQTT stream."

    def test_read_mqtt_single_device_short(self, fix_registered):
        "Test connect to a single device via MQTT and read data."

        import time
        from relayr import Client
        from relayr.resources import Device
        from relayr.dataconnection import MqttStream

        token = fix_registered.testset1['token']
        c = Client(token=token)
        deviceId = fix_registered.testset1['deviceID']
        dev = Device(id=deviceId, client=c)
        received = []

        def callback(topic, payload):
            received.append((topic, payload))

        conn = MqttStream(callback, [dev], transport='mqtt')
        conn.start()
        time.sleep(10)
        conn.stop()
        # dev.delete_channel(creds['channelId'])
        assert len(received) >= 5


@pytest.mark.skipif(True, reason="Needs a CTRL-C to be stopped.")
class TestMqttStreams(object):
    "Test accessing device data via a single topic MQTT stream."

    def test_read_mqtt_single_device(self, fix_registered):
        "Test connect to a single device via MQTT and read data."
        import time
        from relayr import Client
        from relayr.resources import Device
        import paho.mqtt.client as mqtt

        token = fix_registered.testset1['token']
        c = Client(token=token)
        deviceId = fix_registered.testset1['deviceID']
        d = Device(id=deviceId, client=c)

        creds = c.api.post_channel(d.id, 'mqtt')
        print('full channel creds:', creds)
        creds = creds['credentials']

        self.topics = [creds['topic'].encode('utf-8')]

        client = mqtt.Client(client_id=creds['clientId'])
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.on_subscribe = self.on_subscribe
        client.username_pw_set(creds['user'], creds['password'])

        null_file = '/dev/null' if platform.system() != 'Windows' else 'nul'
        client.tls_set(ca_certs=null_file, cert_reqs=ssl.CERT_NONE)
        client.tls_insecure_set(True)

        client.connect('mqtt.relayr.io', port=8883, keepalive=60)
        try:
            client.loop_forever()
        except KeyboardInterrupt:
            print('')

    def on_connect(self, client, userdata, flags, rc):
        for t in self.topics:
            client.subscribe(t)

    def on_subscribe(self, client, userdata, mid, granted_qos):
        pass

    def on_message(self, client, userdata, msg):
        print('received: %s %s' % (msg.topic, msg.payload))

    def receive(self, message, channel):
        "Callback method for data connection."
        print(message)
        self.received_data.append(message)


@pytest.mark.skipif(True, reason="Needs a CTRL-C to be stopped.")
class TestMqttMultipleStreams(object):
    "Test accessing device data via a multiple topics MQTT streams."

    def test_read_mqtt_multi_device(self, fix_registered):
        "Test connect to multiple devices via MQTT and read data."
        import time
        from relayr import Client, Api
        from relayr.resources import Device
        import paho.mqtt.client as mqtt

        token = fix_registered.testset1['token']
        c = Client(token=token)
        deviceId = fix_registered.testset1['deviceID']
        deviceId2 = fix_registered.testset1['deviceID2']

        mic = Device(id=deviceId, client=c)
        mic_creds = c.api.post_channel(mic.id, 'mqtt')
        print('mic channel creds:', mic_creds)
        mic_creds = mic_creds['credentials']

        temphum = Device(id=deviceId2, client=c)
        temphum_creds = c.api.post_channel(temphum.id, 'mqtt')
        print('temphum channel creds:', temphum_creds)
        temphum_creds = temphum_creds['credentials']

        self.topics = [
            mic_creds['topic'].encode('utf-8'),
            temphum_creds['topic'].encode('utf-8')
        ]

        client = mqtt.Client(client_id=mic_creds['clientId'])
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.on_subscribe = self.on_subscribe
        client.username_pw_set(mic_creds['user'], mic_creds['password'])

        null_file = '/dev/null' if platform.system() != 'Windows' else 'nul'
        client.tls_set(ca_certs=null_file, cert_reqs=ssl.CERT_NONE)
        client.tls_insecure_set(True)

        client.connect('mqtt.relayr.io', port=8883, keepalive=60)
        try:
            client.loop_forever()
        except KeyboardInterrupt:
            print('')

    def on_connect(self, client, userdata, flags, rc):
        for t in self.topics:
            client.subscribe(t)

    def on_subscribe(self, client, userdata, mid, granted_qos):
        pass

    def on_message(self, client, userdata, msg):
        print('received: %s %s' % (msg.topic, msg.payload))

    def receive(self, message, channel):
        "Callback method for data connection."
        print(message)
        self.received_data.append(message)


class TestDynmicMqttStreams(object):
    "Test assigning devices to one MQTT stream and reading their data."

    def receive(self, topic, payload):
        "Callback method for receiving device data."
        print('%s %s' % (topic, payload))

    def test_read_mqtt_multi_device_abstract(self, fix_registered):
        "Test add/remove devices dynamically and read their data."
        import time
        from relayr import Client
        from relayr.resources import Device
        from relayr.dataconnection import MqttStream

        fixture = fix_registered.testset1

        c = Client(token=fixture['token'])

        # create channel with one device (microphone)
        mic = Device(id=fixture['deviceID'], client=c)
        stream = MqttStream(self.receive, [mic])
        stream.start()
        time.sleep(5)

        # add one device (temperature/humidity)
        temphum = Device(id=fixture['deviceID2'], client=c)
        stream.add_device(temphum)
        time.sleep(5)

        # remove one device (microphone)
        stream.remove_device(mic)
        time.sleep(5)

        stream.stop()
