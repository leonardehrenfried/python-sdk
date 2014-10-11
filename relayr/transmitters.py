# -*- coding: utf-8 -*-

"""
Relayr transmitter abstractions.

A transmitter (like a Wunderbar) acts as a relayer between devices and 
the cloud.
"""


from relayr import core


class Transmitter(object):
    "A Relayr transmitter."
    
    def __init__(self, transmitterID=None):
        self.transmitterID = transmitterID

    def __repr__(self):
        args = (self.__class__.__name__, self.transmitterID)
        return "%s(transmitterID=%r)" % args

    def get_info(self):
        """
        Get transmitter info.
        
        :rtype: A dict with certain fields.
        """

        if not self.transmitterID:
            raise exceptions.RelayrException('No transmitter ID set, yet.')
        return core.transmitter_get_info(self.transmitterID)

    def update(self, name=None):
        """
        Set transmitter info.
        """

        if not self.transmitterID:
            raise exceptions.RelayrException('No transmitter ID set, yet.')
        return core.transmitter_get_info(self.transmitterID)

    def get_connected_devices(self):
        """
        Return a list of devices connected to this specific transmitter.
        
        :rtype: A list of devices.
        """

        if not self.transmitterID:
            raise exceptions.RelayrException('No transmitter ID set, yet.')
        return core.transmitter_devices(self.transmitterID)
