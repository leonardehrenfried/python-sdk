# -*- coding: utf-8 -*-

"""
This module contains abstractions for relayr API resources.

Resources may be entities such as users, publishers, applications, 
devices, device models and transmitters.
"""


from relayr import exceptions
from relayr.dataconnection import Connection


class User(object):
    "A Relayr user."

    def __init__(self, id=None, client=None):
        self.id = id
        self.client = client

    def __repr__(self):
        return "%s(id=%r)" % (self.__class__.__name__, self.id)

    def get_publishers(self):
        "Return a generator of the publishers of the user."

        for pub_json in self.client.api.get_user_publishers(self.id):
            p = Publisher(pub_json['id'], client=self.client)
            for k in pub_json:
                setattr(p, k, pub_json[k])
            yield p

    def get_apps(self):
        "Returns a generator of the apps of the user."

        for app_json in self.client.api.get_user_apps(self.id):
            ## TODO: change 'app' field to 'id' in API?
            app = App(app_json['app'], client=self.client)
            app.get_info()
            yield app

    def get_transmitters(self):
        "Returns a generator of the transmitters of the user."

        for trans_json in self.client.api.get_user_transmitters(self.id):
            trans = Transmitter(trans_json['id'], client=self.client)
            trans.get_info()
            yield trans

    def get_devices(self):
        "Returns a generator of the devices of the user."

        for dev_json in self.client.api.get_user_devices(self.id):
            dev = Device(dev_json['id'], client=self.client)
            dev.get_info()
            yield dev

    def connect_device(self, app, device, callback):
        "Opens and returns a connection to the data provider."

        creds = self.client.api.post_devices_subscription(app.id, device.id)
        return Connection(callback, creds)

    def connect_public_device(self, device, callback):
        "Opens and returns a connection to the data provider."

        creds = self.client.api.post_devices_public_subscription(device.id)
        return Connection(callback, creds)

    def disconnect_device(self, id):
        # There is no disconnect in the API...
        raise NotImplementedError

    def update(self, name=None, email=None):
        res = self.client.api.patch_user(self.id, name=name, email=email)
        for k in res:
            setattr(self, k, res[k])
        return self

    ## TODO: rename to 'registered_wunderbar_devices'?
    def register_wunderbar(self):
        """
        Returns registered Wunderbar devices (master and sensor modules).
    
        :rtype: A generator over the registered devices and one transmitter.
        """    
        res = self.client.api.post_user_wunderbar(self.id)
        for k, v in res.items():
            if 'model' in v:
                item = Device(res[k]['id'], client=self.client)
                item.get_info()
            else:
                item = Transmitter(res[k]['id'], client=self.client)
                item.get_info()
            yield item

    def remove_wunderbar(self):
        """
        Removes all Wunderbars associated with the user.
        """
        res = self.client.api.post_users_destroy(self.id)
        return res

    def get_bookmarked_devices(self):
        """
        Retrieves a list of bookmarked devices.

        :rtype: list of device objects
        """
        res = self.client.api.get_user_devices_bookmarks(self.id)
        for dev in res:
            d = Device(dev['id'], client=self.client)
            for k, v in dev.items():
                setattr(d, k, v)
            d.get_info()
            yield d

    def bookmark_device(self, device):
        res = self.client.api.post_user_devices_bookmark(self.id, device.id)

    def delete_device_bookmark(self, device):
        res = self.client.api.delete_user_devices_bookmark(self.id, device.id)
        return res


class Publisher(object):
    """
    A relayr publisher.

    A publisher has a few attributes, which can be updated. It can be
    registered to and deleted from the relayr platform. It can list all
    applications it has published on the relayr platform.
    """

    def __init__(self, id=None, client=None):
        self.id = id
        self.client = client

    def __repr__(self):
        return "%s(id=%r)" % (self.__class__.__name__, self.id)

    def get_apps(self, extended=False):
        """
        Get list of apps for this publisher.

        If the optional parameter ``extended`` is ``False`` (default) the 
        response will contain only the fields ``id``, ``name`` and 
        ``description``. If it is ``True`` it will contain additional 
        fields: ``publisher``, ``clientId``, ``clientSecret`` and
        ``redirectUri``.

        :param extended: Flag indicating if the info should be extended.
        :type extended: booloean
        :rtype: A list of :py:class:`relayr.resources.App` objects.
        """

        func = self.client.api.get_publisher_apps
        if extended:
            func = self.client.api.get_publisher_apps_extended
        res = func(self.id)
        for a in res:
            app = App(a['id'], client=self.client)
            app.get_info(extended=extended)
            yield app


    def update(self, name=None):
        """
        Updates certain information fields of the publisher's.
        
        :param name: the user email to be set
        :type name: string
        """
        res = self.api.patch_publisher(self.id, name=name)
        for k in res:
            setattr(self, k, res[k])
        return self

    def register(self, name, id, publisher):
        """
        Adds the publisher to the relayr platform.

        :param name: the publisher name to be set
        :type name: string
        :param id: the publisher UID to be set
        :type id: string
        """
        raise NotImplementedError

    def delete(self):
        """
        Deletes the publisher from the relayr platform.
        """
        res = self.api.delete_publisher(self.id)


class App(object):
    """
    A relayr application.
    
    An application has a few attributes, which can be updated. It can be
    registered to and deleted from the relayr platform. it can be connected 
    to and disconnected from devices.
    """
    
    def __init__(self, id=None, client=None):
        self.id = id
        self.client = client

    def __repr__(self):
        return "%s(id=%r)" % (self.__class__.__name__, self.id)

    def get_info(self, extended=False):
        """
        Get application info.
        
        If the optional parameter ``extended`` is ``False`` (default) the 
        result will contain only the fields ``id``, ``name`` and 
        ``description``. If it is ``True`` it will contain additional 
        fields: ``publisher``, ``clientId``, ``clientSecret`` and
        ``redirectUri``.
        
        :param extended: flag indicating if the info should be extended
        :type extended: booloean
        :rtype: A dict with certain fields.
        """

        func = self.client.api.get_app_info
        if extended:
            func = self.client.api.get_app_info_extended
        res = func(self.id)
        for k in res:
            setattr(self, k, res[k])
        return self

    def update(self, description=None, name=None, redirectUri=None):
        """
        Updates certain fields in the application's description.
        
        :param description: the user name to be set
        :type description: string
        :param name: the user email to be set
        :type name: string
        :param redirectUri: the redirect URI to be set
        :type redirectUri: string
        """
        res = self.client.api.patch_app(self.id, description=description,
            name=name, redirectUri=redirectUri)
        for k in res:
            setattr(self, k, res[k])
        return self

    def delete(self):
        """
        Deletes the app from the relayr platform.
        """
        res = self.api.delete_publisher(self.id)

    def register(self, name, publisher):
        """
        Adds the app to the relayr platform.

        :param name: the app name to be set
        :type name: string
        :param publisher: the publisher to be set
        :type publisher: string(?)
        """
        raise NotImplementedError

    def connect_to_device(self, device):
        """
        Connects the app to a device.
        
        Data reception credentials are returned as part of the response.

        See also the Device.connect_to_device() method...

        :param device: the device (name) to be connected
        :type device: string(?)
        """
        raise NotImplementedError

    def disconnect_from_device(self, device):
        """
        Disonnects the app from a device.

        See also the Device.disconnect_from_app() method...

        :param device: the device (name) to be disconnected from
        :type device: string(?)
        """
        raise NotImplementedError


class Device(object):
    """
    A relayr device.
    """

    def __init__(self, id=None, client=None):
        self.id = id
        self.client = client

    def __repr__(self):
        return "%s(id=%r)" % (self.__class__.__name__, self.id)

    def get_info(self):
        """
        Retrieves device info and stores it as instance attributes.

        :rtype: self.
        """

        res = self.client.api.get_device(self.id)
        for k in res:
            if k == 'model':
                self.model = DeviceModel(res[k]['id'], client=self.client)
                self.model.get_info()
            else:
                setattr(self, k, res[k])
        return self

    def update(self, description=None, name=None, model=None, public=None):
        """
        Updates certain fields in the device description.
        
        :param description: the description to be set
        :type description: string
        :param name: the user name to be set
        :type name: string
        :param model: the device model to be set
        :type name: string?
        :param public: a flag for making the device public
        :type redirectUri: boolean
        """

        res = self.client.api.patch_device(self.id, description=description,
            name=name, model=model, public=public)
        for k in res:
            setattr(self, k, res[k])
        return self

    def get_connected_apps(self):
        """
        Retrieves all apps connected to the device.
        
        :rtype: A list of apps.
        """
        for app_json in self.client.api.get_device_apps(self.id):
            app = App(id=app_json['id'], client=self.client)
            app.get_info()
            yield app

    def connect_to_app(self, app):
        """
        Connects the device to an app.
        
        Data reception credentials are returned as part of the response.

        See also the App.connect_to_device() method...

        :param app: the app (name) to be connected
        :type app: string(?)
        """
        res = self.client.api.post_app_device(app.id, self.id)
        return res

    def disconnect_from_app(self, app):
        """
        Disconnects the device from an app.

        See also the App.disconnect_from_device() method...

        :param app: the app (name) to be disconnected from
        :type app: string(?)
        """
        res = self.client.api.delete_app_device(app.id, self.id)
        return res

    def connect_to_device(self, appID, id, callback):
        """
        Subscribes a user to a device.
        """
        creds = self.client.api.post_devices_subscription(appID, self.id)
        return Connection(callback, creds)

    def connect_to_public_device(self, id, callback):
        """
        Subscribes a user to a public device.

        :param id: the device's UID
        :type id: string
        """

        creds = self.client.api.post_devices_public_subscription(self.id)
        return Connection(callback, creds)

    def send_command(self, command, data):
        """
        Sends a command to the device.

        :param command: the command to be sent
        :type command: string
        :param data: the command data to be sent
        :type data: dict
        """
        
        res = self.client.api.post_device_command(self.id, command, data)
        return res

    def send_data(self, data):
        """
        Sends a data pacakge to the device.

        :param data: the data to be sent
        :type data: dict
        """
        res = self.client.api.post_device_data(self.id, data)
        return res

    def delete(self):
        """
        Deletes the device from the relayr platform.

        :type command: self
        """
        
        res = self.client.api.delete_device(self.id)
        return self

    def switch_led_on(self, bool=True):
        """
        Switches on device's LED for ca. 10 seconds or switches it off.

        :param bool: the desired state, on if True (default), off if False
        :type bool: boolean
        :type command: self
        """
        self.send_command('led', {'cmd': int(bool)})
        return self

class DeviceModel(object):
    """
    relayr device model.
    """
    
    def __init__(self, id=None, client=None):
        self.id = id
        self.client = client

    def __repr__(self):
        return "%s(id=%r)" % (self.__class__.__name__, self.id)

    def get_info(self):
        """
        Returns device model info and stores it as instance attributes.
        
        :rtype: self.
        """
        res = self.client.api.get_device_model(self.id)
        for k, v in res.items():
            setattr(self, k, v)
        return self


class Transmitter(object):
    "A relayr transmitter, The Master Module, for example."
    
    def __init__(self, id=None, client=None):
        self.id = id
        self.client = client

    def __repr__(self):
        args = (self.__class__.__name__, self.id)
        return "%s(id=%r)" % args

    def get_info(self):
        """
        Retrieves transmitter info.
        """
        res = self.client.api.get_transmitter(self.id)
        for k, v in res.items():
            setattr(self, k, v)
        return self

    def delete(self):
        """
        Deletes the transmitter from the relayr platform.

        :type command: self
        """
        
        res = self.client.api.delete_transmitter(self.id)
        return self

    def update(self, name=None):
        """
        Updates transmitter info.
        """
        res = self.client.api.patch_transmitter(self.id, name=name)
        for k, v in res.items():
            setattr(self, k, v)
        return self

    def get_connected_devices(self):
        """
        Returns a list of devices connected to the specific transmitter.
        
        :rtype: A list of devices.
        """
        res = self.client.api.get_transmitter_devices(self.id)
        for d in res:
            dev = Device(d['id'], client=self.client)
            dev.get_info()
            yield dev
