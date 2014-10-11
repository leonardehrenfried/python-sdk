# -*- coding: utf-8 -*-

"""
Relayr applications abstractions.

An application is a collection of permissions...
"""


from relayr import core, exceptions


def get_all_apps():
    """
    Returns a generator over all apps in the Relayr cloud.
    
    This is slightly artificial as long as the called core function always
    returns the entire list already.
    """
    
    all_apps = core.list_all_apps()
    for app in all_apps:
        yield app
        if 0: # later provide real App instances
            a = App(appID=app['id'])
            a.id = app['id']
            if 'name' in app: a.name = app['name']
            if 'description' in app: a.description = app['description']
            yield a


class App(object):
    """
    A Relayr application.
    
    An application has a few attributes, which can be chaged. It can be
    registered to and deleted from the Relayr cloud. And it can be connected 
    to and disconnected from devices.
    """
    
    def __init__(self, appID=None, **context):
        self.appID = appID
        self.context = context

    def __repr__(self):
        return "%s(appID=%r)" % (self.__class__.__name__, self.appID)

    def get_sdk_info(self):
        """
        Return info about the app initiating the request (the one in the token).

        :rtype: A dict with certain fields.
        """

        if not self.appID:
            raise exceptions.RelayrException('No application ID set, yet.')
        res = core.app_get_sdk_info(self.appID, **self.context)
        for k, v in res.iteritems():
            setattr(self, k, v)
        return res


    def get_info(self, extended=False):
        """
        Get application info.
        
        If the optional parameter ``extended`` is ``False`` (default) the 
        result will contain only the fields ``id``, ``name`` and 
        ``description``. If it is ``True`` there will be these additional 
        fields: ``publisher``, ``clientId``, ``clientSecret`` and
        ``redirectUri``.
        
        WARNING: One must be authorized to get the extended info!

        :param extended: flag indicating if the info should be extended
        :type extended: booloean
        :rtype: A dict with certain fields.
        """

        if not self.appID:
            raise exceptions.RelayrException('No application ID set, yet.')
        func = core.app_get_info
        if extended:
            func = core.app_get_info_extended
        res = func(self.appID)
        for k, v in res.items():
            setattr(self, k, v)
        return res


    def update(self, description=None, name=None, redirectUri=None, **context):
        """
        Update certain fields in the application description.
        
        :param description: the user name to be set
        :type description: string
        :param name: the user email to be set
        :type name: string
        :param redirectUri: the redirect URI to be set
        :type redirectUri: string
        """
        if not self.appID:
            raise exceptions.RelayrException('No application ID set, yet.')
        return core.app_patch(self.appID, description=description, name=name, redirectUri=redirectUri, **context)

    def delete(self):
        """
        Delete this app from the Relayr Cloud.
        """
        raise NotImplementedError

    def register(self, name, publisher):
        """
        Add this app to the relayr repository.

        :param name: the app name to be set
        :type name: string
        :param publisher: the publisher to be set
        :type publisher: string(?)
        """
        raise NotImplementedError

    def connect_to_device(self, device):
        """
        Connects this app to a device.
        
        PubNub credentials are returned as part of the response.

        There is also an Device.connect_to_device() method...

        :param device: the device (name) to be connected
        :type device: string(?)
        """
        raise NotImplementedError

    def disconnect_from_device(self, device):
        """
        Disonnect this app from a device.

        There is also an Device.disconnect_from_app() method...

        :param device: the device (name) to be disconnected from
        :type device: string(?)
        """
        raise NotImplementedError

