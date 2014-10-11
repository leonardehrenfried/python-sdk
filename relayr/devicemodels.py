# -*- coding: utf-8 -*-

"""
Relayr device models abstractions.

.. code-block:: python

    from relayr.devicemodels import get_all_devicemodels_meanings
    for dmm in get_all_devicemodels_meanings():
        print(dmm)
    
    {u'value': u'angular speed', u'key': u'angular_speed'}
    {u'value': u'luminosity', u'key': u'luminosity'}
    {u'value': u'acceleration', u'key': u'acceleration'}
    {u'value': u'temperature', u'key': u'temperature'}
    {u'value': u'proximity', u'key': u'proximity'}
    {u'value': u'color', u'key': u'color'}
    {u'value': u'humidity', u'key': u'humidity'}
    {u'value': u'noise level', u'key': u'noise_level'}
"""


from relayr import core, exceptions


def get_all_device_models():
    """
    Returns a generator over all device models in the Relayr cloud.
    
    This is slightly artificial as long as the called core function always
    returns the entire list already.
    """
    
    all_dms = core.list_all_device_models()
    for dm in all_dms:
        yield dm


def get_all_devicemodels_meanings():
    """
    Returns a generator over all device models meanings in the Relayr cloud.
    
    This is slightly artificial as long as the called core function always
    returns the entire list already.
    """
    
    all_devicemodel_meanings = core.list_all_device_model_meanings()
    for dmm in all_devicemodel_meanings:
        yield dmm


class DeviceModel(object):
    "A Relayr device model."
    
    def __init__(self, uuid=None):
        self.uuid = uuid

    def __repr__(self):
        return "%s(uuid=%r)" % (self.__class__.__name__, self.uuid)

    def get_info(self):
        """
        Get device model info.
        
        :rtype: A dict with certain fields.
        """

        if not self.uuid:
            raise exceptions.RelayrException('No device model UUID set, yet.')
        res = core.devicemodel_info(self.uuid)
        for k, v in res.iteritems():
            setattr(self, k, v)
        return res
