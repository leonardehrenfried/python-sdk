# -*- coding: utf-8 -*-

"""
Data Connection Classes

This module provide connection classes for accessing device data.
"""

import ssl
import time
import threading
import platform

from Pubnub import Pubnub
import paho.mqtt.client as mqtt

from relayr import config
from relayr.compat import PY2, PY3


class PubnubDataConnection(threading.Thread):
    "A connection to a PubNub data hub running on its own thread."

    def __init__(self, callback, credentials):
        """
        Opens a PubNub connection with a callback and a credentials dict.

        :param callback: A callable to be called with two arguments:
            message_content and channel_name.
        :type callback: A function or object implementing the ``__call__`` method.
        :param credentials: A set of key/value pairs to be passed to PubNub.
        :type credentials: dict
        """

        super(PubnubDataConnection, self).__init__()
        self._stop_event = threading.Event()
        self.callback = callback
        self.credentials = credentials
        self.channel = credentials['channel']

        self.hub = Pubnub(
            publish_key=credentials.get('publishKey', None),
            subscribe_key=credentials.get('subscribeKey', None),
            cipher_key=credentials.get('cipherKey', None),
            auth_key=credentials.get('authKey', None),
            secret_key=None,
            ssl_on=True
        )

        if PY2 and "daemon" in Pubnub.__init__.func_code.co_varnames:
            self.hub.daemon = True
        elif PY3 and "daemon" in Pubnub.__init__.__code__.co_varnames:
            self.hub.daemon = True

        self.setDaemon(True)

    def run(self):
        """Thread method, called implicitly after starting the thread."""

        self.subscribe(self.channel, self.callback)
        while not self._stop_event.is_set():
            time.sleep(1)

    def stop(self):
        """Mark the connection/thread for being stopped."""

        self._stop_event.set()
        self.unsubscribe(self.channel)

    def subscribe(self, channel_name, callback):
        """
        Subscribes a callable to a channel with the given name.

        :param channel_name: The channel name.
        :type channel_name: string
        :param callback: The callable to be called with two arguments:
            message_content and channel_name.
        :type callback: A function or object implementing the ``__call__`` method.
        """

        self.hub.subscribe(channel_name, callback)

    def unsubscribe(self, channel_name):
        """
        Unsubscribes from a channel with given name.

        :param channel_name: the channel name
        :type channel_name: string
        """

        self.hub.unsubscribe(channel_name)


class MqttStream(threading.Thread):
    "MQTT stream reading data from devices in the relayr cloud."

    def __init__(self, callback, devices, transport='mqtt'):
        """
        Opens an MQTT connection with a callback and one or more devices.

        :param callback: A callable to be called with two arguments:
            the topic and payload of a message.
        :type callback: A function/method or object implementing the ``__call__`` method.
        :param devices: Device objects from which to receive data.
        :type devices: list
        :param transport: Name of the transport method, right now only 'mqtt'.
        :type transport: string
        """
        super(MqttStream, self).__init__()
        self._stop_event = threading.Event()
        self.callback = callback
        self.credentials_list = [dev.create_channel(transport)
            for dev in devices]
        self.topics = [credentials['credentials']['topic']
            for credentials in self.credentials_list]
        self.setDaemon(True)

    def run(self):
        """
        Thread method, called implicitly after starting the thread.
        """
        creds = self.credentials_list[0]['credentials']
        c = self.client = mqtt.Client(client_id=creds['clientId'])
        c.on_connect = self.on_connect
        c.on_disconnect = self.on_disconnect
        c.on_message = self.on_message
        c.on_subscribe = self.on_subscribe
        c.on_unsubscribe = self.on_unsubscribe
        c.username_pw_set(creds['user'], creds['password'])

        # only encryption, no authentication
        c.tls_insecure_set(True)
        null_file = '/dev/null' if platform.system() != 'Windows' else 'nul'
        c.tls_set(ca_certs=null_file, cert_reqs=ssl.CERT_NONE)

        c.connect('mqtt.relayr.io', port=8883, keepalive=60)
        try:
            c.loop_forever()
        except KeyboardInterrupt:
            self.stop()

        while not self._stop_event.is_set():
            time.sleep(1)

    def stop(self):
        """
        Mark the connection/thread for being stopped.
        """
        if not self._stop_event.is_set():
            for t in self.topics:
                self.client.unsubscribe(t.encode('utf-8'))
        self._stop_event.set()
        self.client.disconnect()

    def on_connect(self, client, userdata, flags, rc):
        if not self._stop_event.is_set():
            for t in self.topics:
                self.client.subscribe(t.encode('utf-8'))

    def on_disconnect(self, client, userdata, rc):
        pass

    def on_subscribe(self, client, userdata, mid, granted_qos):
        pass

    def on_unsubscribe(self, client, userdata, mid):
        pass

    def on_message(self, client, userdata, msg):
        self.callback(msg.topic, msg.payload)

    def add_device(self, device):
        "Add a specific device to the MQTT connection to receive data from."
        # create credentials
        creds = device.create_channel('mqtt')
        self.credentials_list.append(creds)
        # extract topic
        topic = creds['credentials']['topic']
        self.topics.append(topic)
        # subscribe topic
        self.client.subscribe(topic.encode('utf-8'))

    def remove_device(self, device):
        "Remove a specific device from the MQTT connection to no longer receive data from."
        # find respective credentials
        dummy_creds = device.create_channel('mqtt')
        creds = [c for c in self.credentials_list
            if c['credentials']['topic'] == dummy_creds['credentials']['topic']][0]
        # remove from self.credentials_list and self.topics
        self.credentials_list.remove(creds)
        topic = creds['credentials']['topic']
        self.topics.remove(topic)
        # unsubscribe topic
        self.client.unsubscribe(topic.encode('utf-8'))


if config.dataConnectionHubName == 'PubNub':
    Connection = PubnubDataConnection
elif config.dataConnectionHubName == 'MQTT':
    Connection = MqttStream
