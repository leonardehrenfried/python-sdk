# -*- coding: utf-8 -*-

"""
Relayr publishers abstractions.

.. code-block:: python

    from relayr import core
    core.publisher_apps(publisherID='f5199c1e-8515-46dc-869c-875688c375c6')
    
    from relayr.publishers import get_all_publishers
    for pub in get_all_publishers():
        print(pub)
    
    from relayr import core
    from relayr.publishers import get_all_publishers
    for i, pub in enumerate(get_all_publishers()):
        apps = core.publisher_apps(publisherID=pub['id'])
        num_apps = len(apps)
        if num_apps > 0:
            print(i, pub['id'], num_apps)
    
    from relayr.publishers import Publisher, get_all_publishers
    for i, pub in enumerate(get_all_publishers()):
        pub = Publisher(publisherID=pub['id'])
        apps = pub.get_apps()
        num_apps = len(apps)
        if num_apps > 0:
            print(i, pub.publisherID, num_apps)
    
    from relayr.publishers import Publisher
    Publisher(publisherID='186b5ea0-7bbf-41e0-a3be-53906a32290e').get_apps()
"""


from relayr import core


def get_all_publishers():
    """
    Returns a generator over all publishers in the Relayr cloud.
    
    This is slightly artificial as long as the called core function always
    returns the entire list already.
    """
    
    all_publishers = core.list_all_publishers()
    for pub in all_publishers:
        yield pub


class Publisher(object):
    """
    A Relayr publisher.

    A publisher has a few attributes, which can be chaged. It can be
    registered to and deleted from the Relayr cloud. And it list all 
    applications it has published in the Relayr cloud.
    """
    
    def __init__(self, publisherID=None):
        self.publisherID = publisherID

    def __repr__(self):
        return "%s(publisherID=%r)" % (self.__class__.__name__, self.publisherID)

    def get_apps(self, extended=False):
        """
        Get list of apps for this publisher.

        If the optional parameter ``extended`` is ``False`` (default) the 
        resulting apps will contain only the fields ``id``, ``name`` and 
        ``description``. If it is ``True`` there will be these additional 
        fields: ``publisher``, ``clientId``, ``clientSecret`` and
        ``redirectUri``.
        
        WARNING: One must be authorized to get the extended info! (?)

        :param extended: flag indicating if the info should be extended
        :type extended: booloean
        :rtype: A list of dicts representing apps.
        """

        if not self.publisherID:
            raise exceptions.RelayrException('No publisher ID set, yet.')
        func = core.publisher_apps
        if extended:
            func = core.publisher_apps_extended
        return func(self.publisherID)

    def update(self, name=None, **context):
        """
        Update certain information fields of the publishers.
        
        :param name: the user email to be set
        :type name: string
        """
        raise NotImplementedError

    def register(self, name, userID, publisher):
        """
        Add this publisher to the relayr repository.

        :param name: the publisher name to be set
        :type name: string
        :param userID: the publisher UID to be set
        :type userID: string(?)
        """
        raise NotImplementedError

    def delete(self):
        """
        Delete this publisher from the Relayr Cloud.
        """
        raise NotImplementedError
