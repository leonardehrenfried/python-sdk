"""

"""

import platform

from relayr import config
from relayr.api import Api
from relayr.version import __version__
from relayr.exceptions import RelayrApiException
from relayr.resources import User, App, Device, DeviceModel, Transmitter, Publisher


class Client(object):
    """
    Relayr client that provides a higher level interface to the Relayr cloud.

    Example:

    .. code-block:: python

        c = Client(token='...')
        info = c.get_oauth_user_info()
        usr = User(info['id'], client=c)
        devs = usr.get_devices()
        d = next(devs)
        apps = usr.get_apps()
    """
    def __init__(self, token=None):
        """
        :arg token: A token generated on the Relayr site for a combination of
            a user and an application.
        :type token: A string.
        """

        self.api = Api(token=token)

    def get_public_apps(self):
        """
        Returns a generator over all apps in the Relayr cloud.

        This is slightly artificial as long as the called API method always
        returns the entire list result and not a paginated one.

        :rtype: A generator for :py:class:`relayr.resources.App` objects.

        .. code-block:: python

            c = Client(token='...')
            apps = c.get_public_apps()
            for app in apps:
                print('%s %s' % (app.id, app.name))
        """

        for app in self.api.get_public_apps():
            a = App(app['id'], client=self)
            a.get_info()
            yield a

    def get_public_publishers(self):
        """
        Returns a generator over all publishers in the Relayr cloud.

        This is slightly artificial as long as the called API method always
        returns the entire list result and not a paginated one.

        :rtype: A generator for :py:class:`relayr.resources.Publisher` objects.
        """

        for pub in self.api.get_public_publishers():
            p = Publisher(pub['id'], client=self)
            for k in pub:
                setattr(p, k, pub[k])
            # p.get_info()
            yield p

    def get_public_devices(self, meaning=''):
        """
        Returns a generator over all devices in the Relayr cloud.

        This is slightly artificial as long as the called API method always
        returns the entire list result and not a paginated one.

        :arg meaning: The *meaning* for the desired devices.
        :type meaning: string
        :rtype: A generator for :py:class:`relayr.resources.Device` objects.
        """

        for dev in self.api.get_public_devices(meaning=meaning):
            d = Device(dev['id'], client=self)
            d.get_info()
            yield d

    def get_public_device_models(self):
        """
        Returns a generator over all device models in the Relayr cloud.

        This is slightly artificial as long as the called API method always
        returns the entire list result and not a paginated one.

        :rtype: A generator for :py:class:`relayr.resources.DeviceModel` objects.
        """

        for dm in self.api.get_public_device_models():
            d = DeviceModel(dm['id'], client=self)
            d.get_info()
            yield d

    def get_public_device_model_meanings(self):
        """
        Returns a generator over all device models meanings in the Relayr cloud.

        A device model meaning is a simple dictionary with a ``key`` and ``value``
        field like this:

        This is slightly artificial as long as the called API method always
        returns the entire list result and not a paginated one.

        :rtype: A device model meaning (as a dictionary) generator.

        .. code-block:: python

            {'key': 'humidity', 'value': 'humidity'}
        """

        for dmm in self.api.get_public_device_model_meanings():
            yield dmm

    def get_user(self):
        """
        Returns the Relayr user belonging to this API client.

        :rtype: A :py:class:`relayr.resources.User` object.
        """
        info = self.api.get_oauth2_user_info()
        usr = User(info['id'], client=self)
        for k in info:
            setattr(usr, k, info[k])
        return usr

    def get_app(self):
        """
        Returns the Relayr application belonging to this API client.

        :rtype: A :py:class:`relayr.resources.App` object.
        """
        info = self.api.get_oauth2_app_info()
        app = App(info['id'], client=self)
        app.get_info()
        return app

    def get_device(self, id):
        """
        Returns the device with the given ID.

        :arg id: the unique ID for the desired device.
        :type id: string
        :rtype: A :py:class:`relayr.resources.Device` object.
        """
        return Device(id=id, client=self)
