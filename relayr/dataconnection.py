# -*- coding: utf-8 -*-

"""
Data Connection

Some initial code to provide connections for different data hubs.
"""

from Pubnub import Pubnub


class PubnubDataConnection(object):
    "..."
    
    def __init__(self, **context):
        "Opens a PubNub connection with credentials from the given context dict."

        self.context = context

        self.hub = Pubnub(
            None, # publish key
            self.context['subscribeKey'],
            cipher_key=self.context['cipherKey'],
            auth_key=self.context['authKey'],
            secret_key=None,
            ssl_on=False
        )
    
    def subscribe(self, channel_name, callback):
        """
        Subscribe a callable to a channel with given name.

        :param channel_name: the channel name
        :type channel_name: string
        :param callback: the callable to be called with two arguments: 
            message_content and channel_name.
        :type callback: function or object implementing the ``__call__`` method.
        :rtype: ``None``
        """
        
        self.hub.subscribe(channel_name, callback)
        # self.hub.timeout(10, callback)
        import time; time.sleep(10)
        print "end of waiting"
        self.hub.unsubscribe(channel_name)
        print "after unsub"
        # self.hub.subscribe(channel_name, None)

    def unsubscribe(self, channel_name):
        """
        Unsubscribe from a channel with given name.

        :param channel_name: the channel name
        :type channel_name: string
        :rtype: ``None``
        """
        
        self.hub.unsubscribe(channel_name)


class MqttDataConnection(object):
    "..."
    
    def __init__(self, **context):
        self.context = context

    def subscribe(self, channel_name, callback):
        raise NotImplementedError

    def unsubscribe(self, channel_name):
        raise NotImplementedError
