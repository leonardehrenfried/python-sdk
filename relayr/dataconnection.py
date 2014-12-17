# -*- coding: utf-8 -*-

"""
Data Connection Classes

This module provide connection classes for accessing device data.
"""

import time
import threading

from Pubnub import Pubnub

from relayr import config


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


class MqttDataConnection(object):
    "..."
    
    def __init__(self, callback, credentials):
        pass

    def subscribe(self, channel_name, callback):
        raise NotImplementedError

    def unsubscribe(self, channel_name):
        raise NotImplementedError


if config.dataConnectionHubName == 'PubNub':
    Connection = PubnubDataConnection
elif config.dataConnectionHubName == 'MQTT':
    Connection = MqttDataConnection
