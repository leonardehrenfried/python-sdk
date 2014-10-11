# -*- coding: utf-8 -*-

"""
Relayr device abstractions.
"""


from relayr import core, exceptions


def get_all_devices(meaning=''):
    """
    Returns a generator over all devices in the Relayr cloud.
    
    This is slightly artificial as long as the called core function always
    returns the entire list already.
    """
    
    all_devices = core.list_all_public_devices(meaning=meaning)
    for d in all_devices:
        yield d


class Device(object):
    """
    A Relayr device.
    """
    
    def __init__(self, deviceID=None, **context):
        self.deviceID = deviceID
        self.context = context

    def __repr__(self):
        return "%s(deviceID=%r)" % (self.__class__.__name__, self.deviceID)

    def get_info(self):
        """
        Get device info.

        :rtype: A dict with certain fields.
        """

        if not self.deviceID:
            raise exceptions.RelayrException('No device UUID set, yet.')
        res = core.device(self.deviceID, **self.context)
        for k, v in res.iteritems():
            setattr(self, k, v)
        return res

    def get_connected_apps(self):
        """
        Get all apps connected to this device.
        
        :rtype: A list of apps.
        """

        if not self.deviceID:
            raise exceptions.RelayrException('No device UUID set, yet.')
        res = core.device_apps(self.deviceID, **self.context)
        return res

    def connect_to_app(self, app):
        """
        Connect this device to an app.
        
        PubNub credentials are returned as part of the response.

        There is also an App.connect_to_device() method...

        :param app: the app (name) to be connected
        :type app: string(?)
        """
        raise NotImplementedError

    def disconnect_from_app(self, app):
        """
        Disconnect this device from an app.

        There is also an App.disconnect_from_device() method...

        :param app: the app (name) to be disconnected from
        :type app: string(?)
        """
        raise NotImplementedError

    ## TODO: This should rather be on the User, shouldn't it?
    def connect_to_public_device(self, deviceID, callback):
        """
        Subscribe a user to a public device.

        :param deviceID: the device's UID
        :type deviceID: string

        """
        res = core.user_connect_public_device(deviceID, callback)
        ## TODO: should return a connection object with preset credentials...
        return res

    def send_command(self, command):
        """
        Send a command to this device.

        :param command: the command to be sent
        :type command: string
        """
        
        if not self.deviceID:
            raise exceptions.RelayrException('No device UUID set, yet.')
        res = core.device_command(self.deviceID, command, **self.context)
        return res

