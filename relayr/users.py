# -*- coding: utf-8 -*-

"""
Relayr user abstractions.

A user is somebody with an account on the Relayr cloud.
"""


from relayr import core
from relayr.devices import Device


class User(object):
    "A Relayr user."

    def __init__(self, userID=None, **context):
        self.userID = userID
        self.context = context

    def __repr__(self):
        return "%s(userID=%r)" % (self.__class__.__name__, self.userID)

    def get_publishers(self):
        return core.user_publishers(self.userID, **self.context)

    def get_apps(self):
        return core.user_apps(self.userID, **self.context)

    def get_transmitters(self):
        return core.user_transmitters(self.userID, **self.context)

    def get_devices(self):
        return core.user_devices(self.userID, **self.context)
        
    def connect_device(self, deviceID, callback):
        return core.user_connect_public_device(deviceID, callback, **self.context)

    def disconnect_device(self, deviceID):
        return core.user_disconnect_public_device(deviceID, **self.context)

    def update_details(self):
        raise NotImplementedError

    def register_wunderbar(self):
        """
        Return the IDs and Secrets of the Master Module and Sensor Modules.
    
        :param userID: the users's UID
        :type userID: string
        :rtype: a list of initialized master and sensor devices
        """    
        res = core.user_wunderbar(self.userID, **self.context)
        # return res
        devices = []
        for k in res.keys():
            self.context['deviceID'] = res[k]['id']
            dev = Device(**self.context)
            dev.get_info()
            devices.append(dev)
        return devices

    def remove_wunderbar(self):
        """
        Remove all Wunderbars associated with this user.
    
        :param userID: the users's UID
        :type userID: string
        """    
        res = core.user_wunderbar_remove_all(self.userID, **self.context)
        return res
