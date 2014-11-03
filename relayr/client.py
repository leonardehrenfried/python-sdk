"""

"""

import platform

from relayr.api import Api
from relayr.version import __version__
from relayr.exceptions import RelayrApiException
from relayr.resources import User, App, Device, DeviceModel, Transmitter, Publisher


DEBUG = True

_userAgent = 'Python-Relayr-Client/{version} ({plat}; {pyimpl} {pyver})'.format(
    version=__version__,
    plat=platform.platform(),
    pyimpl=platform.python_implementation(),
    pyver=platform.python_version(),
)


class Client(object):
    """
    Relayr client that provides a higher level interface to the Relayr cloud.

    Some examples:

    .. code-block:: python

        # ...
        c = Client(token='...')
        info = c.get_oauth_user_info()
        usr = User(info['id'], client=c)
        devs = usr.get_devices()
        d = devs.next()
        apps = usr.get_apps()
    """
    def __init__(self, host=None, token=None):
        """
        :arg host: the base url for accessing the Relayr RESTful API, default
            is ``https://api.relayr.io``.

        :arg token: a token generated on the Relayr site for a combination of 
            a user and an application.
        """

        self.host = host or 'https://api.relayr.io'
        self.token = token
        self.useragent = _userAgent
        self.headers = {
            'User-Agent': self.useragent,
            'Content-Type': 'application/json'
        }
        if self.token:
            self.headers['Authorization'] = 'Bearer {0}'.format(self.token)
        self.api = Api(host, token=self.token)

    def get_public_apps(self):
        """
        Returns a generator over all apps in the Relayr cloud.

        This is slightly artificial as long as the called API method always
        returns the entire list result and not a paginated one.

        .. code-block:: python

            c = Client(token='...')
            all_apps = c.get_public_apps()
            for app in all_apps:
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
        """

        for dm in self.api.get_public_device_models():
            d = DeviceModel(dm['id'], client=self)
            d.get_info()
            yield d

    def get_public_device_model_meanings(self):
        """
        Returns a list of all device models meanings in the Relayr cloud.

        A device model meaning is a simple dictionary with a ``key`` and ``value``
        field like this:

        .. code-block:: python

            {'key': 'humidity', 'value': 'humidity'}

        This is slightly artificial as long as the called API method always
        returns the entire list result and not a paginated one.
        """

        for dmm in self.api.get_public_device_model_meanings():
            yield dmm

    def get_user(self):
        """Returns the user belonging to this API client."""
        info = self.api.get_oauth2_user_info()
        usr = User(info['id'], client=self)
        for k in info:
            setattr(usr, k, info[k])
        return usr

    def get_app(self):
        """Returns the application belonging to this API client."""
        info = self.api.get_oauth2_app_info()
        app = App(info['id'], client=self)
        app.get_info()
        return app

    def get_device(self, id):
        """Returns the device with the given ID."""
        return Device(id=id, client=self)
