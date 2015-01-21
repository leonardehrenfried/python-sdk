"""
Implementation of the relayr API as individual endpoints.

This module contains the API class with one method for each API endpoint.
All method names start with the HTTP method followed by the resource name used
in that endpoint e.g. ``post_user_app`` for the endpoint
``POST /users/<id>/apps/<id>`` with minor modifications.
"""

import os
import time
import json
import platform
import urllib
import warnings
import logging

import requests

from relayr import config
from relayr.version import __version__
from relayr.exceptions import RelayrApiException
from relayr.compat import urlencode


def create_logger(sender):
    "Create a logger for the requesting object."

    logger = logging.getLogger('Relayr API Client')
    logger.setLevel(logging.DEBUG)

    logfile = "{0}/relayr-api-{1}.log".format(config.LOG_DIR, id(sender))
    h = logging.FileHandler(logfile)
    # h = logging.RotatingFileHandler(logfile,
    #     mode='a', maxBytes=2**14, backupCount=5, encoding=None, delay=0)

    # h.setLevel(logging.DEBUG)

    # create formatter and add it to the handler(s)
    fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt, '%Y-%m-%d %H:%M:%S.%f %Z%z')
    formatter.converter = time.gmtime
    h.setFormatter(formatter)

    # add the handler(s) to the logger
    logger.addHandler(h)

    return logger

def build_curl_call(method, url, data=None, headers=None):
    """
    Builds and returns a ``curl`` command for use on the command-line.

    :param method: HTTP request method, ``GET``, ``POST``, etc.
    :type method: string
    :param url: Full HTTP path.
    :type url: string
    :param data: Data to be transmitted, usually *posted*.
    :type data: object serializable as JSON
    :param headers: Additional HTTP request headers.
    :type headers: dictionary
    :rtype: string

    Example:

    .. code-block:: python

        cmd = build_curl_call('POST', 'http://foo.com/bar', data={'x': 42},
                headers={'SUPER_SECRET_KEY': '123'})
        print(cmd)
        curl -X POST http://foo.com/bar -H "SUPER_SECRET_KEY: 123" --data "{\"x\": 42}"
    """

    command = "curl -X {0} {1}".format(method.upper(), url)
    if headers:
        for k, v in headers.items():
            command += ' -H "{0}: {1}"'.format(k, v)
    if data:
        jsdata = json.dumps(data)
        command += " --data {0}".format(json.dumps(jsdata))
    return command

class Api(object):
    """
    This class provides direct access to the relayr API endpoints.

    Examples:

    .. code-block:: python

        # Creates an anonymous client and calls simple API endpoints:
        from relayr.api import Api
        a = Api()
        assert a.get_server_status() == {'database': 'ok'}
        assert a.get_users_validate('god@in.heaven') == {'exists': False}
        assert a.get_public_device_model_meanings() > 0

    """
    def __init__(self, token=None):
        """
        :arg token: a token generated on the relayr site for a combination of
            a relayr user and application.
        """

        self.token = token
        self.host = config.relayrAPI
        self.useragent = config.userAgent
        self.headers = {
            'User-Agent': self.useragent,
            'Content-Type': 'application/json'
        }
        if self.token:
            self.headers['Authorization'] = 'Bearer {0}'.format(self.token)

        if config.LOG:
            self.logger = create_logger(self)
            self.logger.info('started')

        # check if the API is available
        try:
            self.get_server_status()
        except:
            raise

    def __del__(self):
        """Object destruction..."""
        if config.LOG:
            self.logger.info('terminated')

    def perform_request(self, method, url, data=None, headers=None):
        """
        Performs an API call and returns a JSON result as Python datastructure.

        Query parameters are expected in the ``url`` parameter.
        For returned status codes other than 2XX a ``RelayrApiException``
        is raised which contains the API call (method and URL) plus
        a ``curl`` command replicating the API call for debugging reuse
        on the command-line.
        """

        if config.LOG:
            command = build_curl_call(method, url, data, headers)
            self.logger.info("API request: " + command)

        urlencoded_data = None
        json_data = 'null'
        if data is not None:
            urlencoded_data = urlencode(data)
            json_data = json.dumps(data)
            try:
                json_data = json_data.encode('utf-8')
            except (UnicodeDecodeError, AttributeError):
                # bytes/str - no need to re-encode
                pass

        func = getattr(requests, method.lower())
        resp = func(url, data=json_data or '', headers=headers or {})
        resp.connection.close()

        if config.LOG:
            hd = dict(resp.headers.items())
            self.logger.info("API response headers: " + json.dumps(hd))
            self.logger.info("API response content: " + resp.content)

        status = resp.status_code
        if 200 <= status < 300:
            try:
                js = resp.json()
            except:
                js = None
                # raise ValueError('Invalid JSON code(?): %r' % resp.content)
                if config.DEBUG:
                    warnings.warn("Replaced suspicious API response (invalid JSON?) %r with 'null'!" % resp.content)
            return status, js
        else:
            args = (resp.json()['message'], method.upper(), url)
            msg = "{0} - {1} {2}".format(*args)
            command = build_curl_call(method, url, data, headers)
            msg = "%s - %s" % (msg, command)
            raise RelayrApiException(msg)


    # ..............................................................................
    # System
    # ..............................................................................

    def get_users_validate(self, userEmail):
        """
        Validate a user email address.

        :param userEmail: The user email address to be validated.
        :type userEmail: string
        :rtype: A dict with an ``exists`` field and a Boolean result value.

        Sample result::

            {"exists": True}
        """

        # https://api.relayr.io/users/validate?email=<userEmail>
        url = '{0}/users/validate?email={1}'.format(self.host, userEmail)
        _, data = self.perform_request('GET', url, headers=self.headers)
        return data

    def get_server_status(self):
        """
        Queries server status.

        :rtype: A dict with certain fields describing the server status.

        Sample result::

            {"database": "ok"}
        """

        # https://api.relayr.io/server-status
        url = '{0}/server-status'.format(self.host)
        _, data = self.perform_request('GET', url, headers=self.headers)
        return data

    def post_oauth2_token(self, clientID, clientSecret, code, redirectURI):
        """
        User:token from tmp code. (?)

        Generates a user token from supplied parameters
        """

        data = {
            "client_id": clientID,
            "client_secret": clientSecret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirectURI
        }

        # https://api.relayr.io/oauth2/token
        url = '{0}/oauth2/token'.format(self.host)
        _, data = self.perform_request('POST', url, data=data, headers=self.headers)
        return data

    def get_oauth2_appdev_token(self, appID):
        """
        Retrieves a token representing a specific relayr application and user.

        :param appID: The application's UUID.
        :type appID: string
        :rtype: A dict with fields describing the token.

        Sample result (anonymized token value)::

            {
                "token": "...",
                "expiryDate": "2014-10-08T10:14:07.789Z"
            }
        """

        # https://api.relayr.io/oauth2/appdev-token/<appID>
        url = '{0}/oauth2/appdev-token/{1}'.format(self.host, appID)
        _, data = self.perform_request('GET', url, headers=self.headers)
        return data

    def post_oauth2_appdev_token(self, appID):
        """
        Generates a new token representing a user and a relayr Application.

        :param appID: The application's UUID.
        :type appID: string
        :rtype: A dict with fields describing the token.
        """

        # https://api.relayr.io/oauth2/appdev-token/<appID>
        url = '{0}/oauth2/appdev-token/{1}'.format(self.host, appID)
        _, data = self.perform_request('POST', url, headers=self.headers)
        return data

    def delete_oauth2_appdev_token(self, appID):
        """
        Revokes token.

        :param appID: The application's UUID.
        :type appID: string
        """

        # https://api.relayr.io/oauth2/appdev-token/<appID>
        url = '{0}/oauth2/appdev-token/{1}'.format(self.host, appID)
        _, data = self.perform_request('DELETE', url, headers=self.headers)
        return data

    # ..............................................................................
    # Users
    # ..............................................................................

    def get_oauth2_user_info(self):
        """
        Returns information about the user initiating the request.

        :rtype: A dictionary with fields describing the user.

        Sample result (partly anonymized values)::

            {
                "email": "joe@foo.com",
                "id": "...",
                "name": "joefoo"
            }
        """

        # https://api.relayr.io/oauth2/user-info
        url = '{0}/oauth2/user-info'.format(self.host)
        _, data = self.perform_request('GET', url, headers=self.headers)
        return data

    def patch_user(self, userID, name=None, email=None):
        """
        Updates one or more user attributes.

        :param userID: the users's UUID
        :type userID: string
        :param name: the user name to be set
        :type name: string
        :param email: the user email to be set
        :type email: string
        :rtype: dict with user info fields
        """

        data = {}
        if name is not None:
            data.update(name=name)
        if email is not None:
            data.update(email=email)

        # https://api.relayr.io/users/%s
        url = '{0}/users/{1}'.format(self.host, userID)
        _, data = self.perform_request('PATCH', url, data=data, headers=self.headers)
        return data

    def post_user_app(self, userID, appID):
        """
        Installs a new app under a specific user.

        :param userID: the users's UUID
        :type userID: string
        :param appID: The application's UUID.
        :type appID: string
        """

        # https://api.relayr.io/users/%s/apps/%s
        url = '{0}/users/{1}/apps/{2}'.format(self.host, userID, appID)
        _, data = self.perform_request('POST', url, headers=self.headers)
        return data

    def delete_user_app(self, userID):
        """
        Uninstalls an app of a specific user.

        :param userID: the users's UUID
        :type userID: string
        """

        # https://api.relayr.io/users/%s/apps/%s
        url = '{0}/users/{1}/apps/{2}'.format(self.host, userID, appID)
        _, data = self.perform_request('DELETE', url, headers=self.headers)
        return data

    def get_user_publishers(self, userID):
        """
        Returns all publishers owned by a specific user.

        :param userID: the users's UUID
        :type userID: string
        :rtype: list of dicts representing publishers
        """

        # https://api.relayr.io/users/%s/publishers
        url = '{0}/users/{1}/publishers'.format(self.host, userID)
        _, data = self.perform_request('GET', url, headers=self.headers)
        return data

    def get_user_apps(self, userID):
        """
        Returns all apps installed under a specific user.

        :param userID: the users's UUID
        :type userID: string
        :rtype: list of dicts ... with IDs and secrets
        """

        # https://api.relayr.io/users/%s/apps
        url = '{0}/users/{1}/apps'.format(self.host, userID)
        _, data = self.perform_request('GET', url, headers=self.headers)
        return data

    def get_user_transmitters(self, userID):
        """
        Returns all transmitters under a specific user.

        :param userID: the users's UUID
        :type userID: string
        :rtype: list of dicts with IDs and secrets
        """

        # https://api.relayr.io/users/%s/transmitters
        url = '{0}/users/{1}/transmitters'.format(self.host, userID)
        _, data = self.perform_request('GET', url, headers=self.headers)
        return data

    def get_user_devices(self, userID):
        """
        Returns all devices registered under a specific user.

        :param userID: the users's UUID
        :type userID: string
        :rtype: list of dicts ...
        """

        # https://api.relayr.io/users/%s/devices
        url = '{0}/users/{1}/devices'.format(self.host, userID)
        _, data = self.perform_request('GET', url, headers=self.headers)
        return data

    def get_user_devices_filtered(self, userID, meaning):
        """
        Returns all devices registered under a specific user filtered by meaning.

        :param userID: the users's UUID
        :type userID: string
        :param meaning: a meaning used for filtering results
        :type meaning: string
        :rtype: list of dicts representing devices
        """

        # https://api.relayr.io/users/%s/devices?meaning=%s
        url = '{0}/users/{1}/devices?meaning={2}'.format(self.host, userID, meaning)
        _, data = self.perform_request('GET', url, headers=self.headers)
        return data

    def get_user_devices_bookmarks(self, userID):
        """
        Returns a list of devices bookmarked by the specific user.

        :param userID: the users's UUID
        :type userID: string
        :rtype: list of dicts, each representing a device

        Sample result (anonymized IDs)::

            [{u'firmwareVersion': u'1.0.0',
              u'id': '...',
              u'model': '...',
              u'name': 'My Wunderbar Microphone',
              u'owner': '...',
              u'public': True,
              u'secret': '238885'}]
        """

        # https://api.relayr.io/users/%s/devices/bookmarks
        url = '{0}/users/{1}/devices/bookmarks'.format(self.host, userID)
        _, data = self.perform_request('GET', url, headers=self.headers)
        return data

    def post_user_devices_bookmark(self, userID, deviceID):
        """
        Bookmarks a specific public device for a user.

        :param userID: the users's UUID
        :type userID: string
        :param deviceID: the UUID of the device to be bookmarked
        :type deviceID: string
        :rtype: list of dicts ...

        Sample result (anonymized IDs)::

            {'createdAt': '2014-11-05T16:31:06.429Z',
             'deviceId': '...',
             'userId': '...'}
         """

        # https://api.relayr.io/users/%s/devices/bookmarks
        url = '{0}/users/{1}/devices/{2}/bookmarks'.format(self.host, userID, deviceID)
        _, data = self.perform_request('POST', url, headers=self.headers)
        return data

    def delete_user_devices_bookmark(self, userID, deviceID):
        """
        Deletes a bookmark for a user and a device.

        :param userID: the users's UUID
        :type userID: string
        :param deviceID: the device's UUID
        :type deviceID: string
        :rtype: None
        """

        # https://api.relayr.io/users/%s/devices/%s/bookmarks
        url = '{0}/users/{1}/devices/{2}/bookmarks'.format(self.host, userID, deviceID)
        _, data = self.perform_request('DELETE', url, headers=self.headers)
        return data

    def post_user_wunderbar(self, userID):
        """
        Returns the IDs and Secrets of the Master Module and Sensor Modules.

        :param userID: the users's UUID
        :type userID: string
        :rtype: dict with information about master and sensor modules/devices

        Sample result (abbreviated, some values anonymized)::

            {
                "bridge": { ... },
                "microphone": {
                    "name": "My Wunderbar Microphone",
                    "public": False,
                    "secret": "......",
                    "owner": "...",
                    "model": {
                        "readings": [
                            {
                                "meaning": "noise_level",
                                "unit": "dba"
                            }
                        ],
                        "manufacturer": "Relayr GmbH",
                        "id": "...",
                        "name": "Wunderbar Microphone"
                    },
                    "id": "...",
                    "firmwareVersion": "1.0.0"
                },
                "light": { ... },
                "masterModule": {
                    "owner": "...",
                    "secret": "............",
                    "id": "...",
                    "name": "My Wunderbar Master Module"
                },
                "infrared": { ... },
                "thermometer": { ... },
                "gyroscope": { ... }
            }
        """

        # https://api.relayr.io/users/%s/wunderbar
        url = '{0}/users/{1}/wunderbar'.format(self.host, userID)
        _, data = self.perform_request('POST', url, headers=self.headers)
        return data

    def delete_wunderbar(self, transmitterID):
        """
        Removes a Wunderbar identified by its master module. This means
        that in addition to the transmitter (the master module) all associated
        devices (sensors) are being deleted.

        :param transmitterID: the UID of the master module
        :type transmitterID: string
        """

        # https://api.relayr.io/wunderbars/%s
        url = '{0}/wunderbars/{1}'.format(self.host, transmitterID)
        _, data = self.perform_request('DELETE', url, headers=self.headers)
        return data

    def post_users_destroy(self, userID):
        """
        Removes all Wunderbars associated with a specific user.

        :param userID: the users's UUID
        :type userID: string
        """

        # https://api.relayr.io/users/%s/destroy-everything-i-love
        url = '{0}/users/{1}/destroy-everything-i-love'.format(self.host, userID)
        _, data = self.perform_request('POST', url, headers=self.headers)
        return data

    # ..............................................................................
    # Applications
    # ..............................................................................

    def get_public_apps(self):
        """
        Returns a list of all applications on the relayr platform

        :rtype: list of dicts, each representing a relayr application
        """

        # https://api.relayr.io/apps
        url = '{0}/apps'.format(self.host)
        _, data = self.perform_request('GET', url, headers=self.headers)
        return data

    def post_app(self, appName, publisherID, redirectURI, appDescription):
        """
        Registers a new app to the relayr platform.

        :rtype: list of dicts, each representing a relayr application
        """

        data = {
          "name": appName,
          "publisher": publisherID,
          "redirectUri": redirectURI,
          "description": appDescription
        }
        # https://api.relayr.io/apps
        url = '{0}/apps'.format(self.host)
        _, data = self.perform_request('POST', url, data=data, headers=self.headers)
        return data

    def get_app_info(self, appID):
        """
        Returns information about the app with the given ID.

        Sample result (anonymized token value)::

            {
                "id": "...",
                "name": "My App",
                "description": "My Wunderbar app",
                ...
            }
        """

        # https://api.relayr.io/apps/<appID>
        url = '{0}/apps/{1}'.format(self.host, appID)
        _, data = self.perform_request('GET', url, headers=self.headers)
        return data

    def get_app_info_extended(self, appID):
        """
        Returns extended information about the app with the given ID.

        Sample result (some values anonymized)::

            {
                "id": "...",
                "name": "My App",
                "publisher": "...",
                "clientId": "...",
                "clientSecret": "...",
                "description": "My Wunderbar app",
                "redirectUri": https://relayr.io
            }
        """

        # https://api.relayr.io/apps/<appID>/extended
        url = '{0}/apps/{1}/extended'.format(self.host, appID)
        _, data = self.perform_request('GET', url, headers=self.headers)
        return data


    def patch_app(self, appID, description=None, name=None, redirectUri=None):
        """
        Updates one or more app attributes.

        :param appID: the application's UID
        :type appID: string
        :param description: the user name to be set
        :type description: string
        :param name: the user email to be set
        :type name: string
        :param redirectUri: the redirect URI to be set
        :type redirectUri: string

        Sample result (some values anonymized)::

            {
                "id": "...",
                "name": "My App",
                "publisher": "...",
                "clientId": "...",
                "clientSecret": "...",
                "description": "My Wunderbar app",
                "redirectUri": https://relayr.io
            }
        """

        data = {}
        if name is not None:
            data.update(name=name)
        if description is not None:
            data.update(description=description)
        if redirectUri is not None:
            data.update(redirectUri=redirectUri)

        # https://api.relayr.io/apps/<appID>
        url = '{0}/apps/{1}'.format(self.host, appID)
        _, data = self.perform_request('PATCH', url, data=data, headers=self.headers)
        return data

    def delete_app(self, appID):
        """
        Deletes an app from the relayr platform.

        :param appID: the application's UID
        :type appID: string
        """

        # https://api.relayr.io/apps/<appID>
        url = '{0}/apps/{1}'.format(self.host, appID)
        _, data = self.perform_request('DELETE', url, headers=self.headers)
        return data

    def get_oauth2_app_info(self):
        """
        Returns info about the app initiating the request (the one in the token).

        Sample result (anonymized token value)::

            {
                "id": "...",
                "name": "My App",
                "description": "My Wunderbar app"
            }
        """

        # https://api.relayr.io/oauth2/app-info
        url = '{0}/oauth2/app-info'.format(self.host)
        _, data = self.perform_request('GET', url, headers=self.headers)
        return data

    def post_app_device(self, appID, deviceID):
        """
        Connects an app to a device. Credentials are returned as part of the response.
        """
        # {{relayrAPI}}/apps/{{appID}}/devices/{{deviceID}}
        url = '{0}/apps/{1}/devices/{2}'.format(self.host, appID, deviceID)
        _, data = self.perform_request('POST', url, headers=self.headers)
        return data

    def delete_app_device(self, appID, deviceID):
        """
        Disconnect an app from a device.
        """
        # {{relayrAPI}}/apps/{{appID}}/devices/{{deviceID}}
        url = '{0}/apps/{1}/devices/{2}'.format(self.host, appID, deviceID)
        _, data = self.perform_request('DELETE', url, headers=self.headers)
        return data

    # ..............................................................................
    # Publishers
    # ..............................................................................

    def get_public_publishers(self):
        """
        Returns a list of all publishers on the relayr platform.

        :rtype: list of dicts, each representing a relayr publisher
        """

        # https://api.relayr.io/publishers
        url = '{0}/publishers'.format(self.host)
        _, data = self.perform_request('GET', url, headers=self.headers)
        return data

    def post_publisher(self, userID, name):
        """
        Registers a new publisher.

        :param userID: the user UID of the publisher
        :type userID: string
        :param name: the publisher name
        :type name: string
        :rtype: a dict with fields describing the new publisher
        """

        # https://api.relayr.io/publishers
        data = {'owner': userID, 'name': name}
        url = '{0}/publishers'.format(self.host)
        _, data = self.perform_request('POST', url, data=data, headers=self.headers)
        return data

    def delete_publisher(self, publisherID):
        """
        Deletes a specific publisher from the relayr platform.

        :param publisherID: the publisher UID
        :type publisherID: string
        :rtype: an empty dict(?)
        """

        # https://api.relayr.io/publishers
        url = '{0}/publishers/{1}'.format(self.host, publisherID)
        _, data = self.perform_request('DELETE', url, headers=self.headers)
        return data

    def get_publisher_apps(self, publisherID):
        """
        Returns a list of apps published by a specific publisher.

        :rtype: A list of apps.
        """

        # https://api.relayr.io/publishers/<id>/apps
        url = '{0}/publishers/{1}/apps'.format(self.host, publisherID)
        _, data = self.perform_request('GET', url, headers=self.headers)
        return data

    def get_publisher_apps_extended(self, publisherID):
        """
        Returns a list with extended information about the publisher's apps.

        :rtype: A list of apps.
        """

        # https://api.relayr.io/publishers/<id>/apps/extended
        url = '{0}/publishers/{1}/apps/extended'.format(self.host, publisherID)
        _, data = self.perform_request('GET', url, headers=self.headers)
        return data


    def patch_publisher(self, publisherID, name=None):
        """
        Updates one or more publisher attributes.

        :param publisherID: the publisher's UID
        :type publisherID: string
        :param name: the publisher name to be set
        :type name: string
        :rtype: ``True``, if successful, ``False`` otherwise
        """

        data = {}
        if name is not None:
            data.update(name=name)

        # https://api.relayr.io/publishers/<id>
        url = '{0}/publishers/{1}'.format(self.host, publisherID)
        _, data = self.perform_request('PATCH', url, data=data, headers=self.headers)
        return data

    # ..............................................................................
    # Devices
    # ..............................................................................

    def get_device_configuration(self, deviceID):
        """
        Returns the device's configuration, default values and schema.

        Example result::

            {
                "version": "1.0.0",
                "configuration": {
                    "defaultValues": {
                        "frequency": 1000
                    },
                    "schema": {
                        "required": [
                            "frequency"
                        ],
                        "type": "object",
                        "properties": {
                            "frequency": {
                                "minimum": 5,
                                "type": "integer",
                                "description": "Frequency of the sensor updates in milliseconds"
                            }
                        },
                        "title": "Relayr configuration schema"
                    }
                }
            }

        :param deviceID: the device UID
        :type deviceID: string
        """

        # https://api.relayr.io/devices/<deviceID>/firmware
        url = '{0}/devices/{1}/firmware'.format(self.host, deviceID)
        _, data = self.perform_request('GET', url, headers=self.headers)
        return data

    def post_device_configuration(self, deviceID, frequency):
        """
        Modifies the configuration of a specific device facillitated by a schema.

        :param deviceID: the device UID
        :type deviceID: string
        :param frequency: the number of ms between two sensor transmissions
        :type frequency: integer
        """

        data = {'frequency': frequency}
        # https://api.relayr.io/devices/<deviceID>/configuration
        url = '{0}/devices/{1}/configuration'.format(self.host, deviceID)
        _, data = self.perform_request('POST', url, data=data, headers=self.headers)
        return data

    def get_public_devices(self, meaning=''):
        """
        Returns list of all public devices on the relayr platform.

        :param meaning: required meaning in the device model's ``readings`` attribute
        :type meaning: string
        :rtype: list of dicts, each representing a relayr device
        """

        # https://api.relayr.io/devices/public
        url = '{0}/devices/public'.format(self.host)
        if meaning:
            url += '?meaning={0}'.format(meaning)
        _, data = self.perform_request('GET', url)
        return data

    def post_device(self, name, owner, modelId, firmwareVersion):
        """
        Registers a new device on the relayr platform.

        :rtype: list of dicts, each representing a relayr device
        """

        data = {
          "name": name,
          "owner": owner,
          "model": modelId,
          "firmwareVersion": firmwareVersion
        }
        # https://api.relayr.io/devices
        url = '{0}/devices'.format(self.host)
        _, data = self.perform_request('POST', url, data=data, headers=self.headers)
        return data

    def get_device(self, deviceID):
        """
        Returns information about a specific device.

        :param deviceID: the device UID
        :type deviceID: string
        :rtype: a dict with fields containing information about the device

        Raises ``exceptions.RelayrApiException`` for invalid UIDs or missing
        credentials...
        """

        # https://api.relayr.io/devices/%s
        url = '{0}/devices/{1}'.format(self.host, deviceID)
        _, data = self.perform_request('GET', url, headers=self.headers)
        return data

    def patch_device(self, deviceID=None, deviceName=None, deviceDescription=None, deviceModel=None, isDevicePublic=None):
        """
        Updates one or more device attributes.

        :param deviceID: the device UID
        :type deviceID: string
        :rtype: a dict with fields containing information about the device

        Raises ``exceptions.RelayrApiException`` for invalid UIDs or missing
        credentials...
        """

        data = {
          "name": deviceName,
          "description": deviceDescription,
          "model": deviceModel,
          "public": isDevicePublic
        }
        for k, v in data.items():
            if v is None:
                del data[k]
        # https://api.relayr.io/devices/%s
        url = '{0}/devices/{1}'.format(self.host, deviceID)
        _, data = self.perform_request('PATCH', url, data=data, headers=self.headers)
        return data

    def delete_device(self, deviceID):
        """
        Deletes a device from the relayr plarform.

        :param deviceID: the device UID
        :type deviceID: string
        :rtype: a dict with fields containing information about the device
        """
        # https://api.relayr.io/devices/%s
        url = '{0}/devices/{1}'.format(self.host, deviceID)
        _, data = self.perform_request('DELETE', url, headers=self.headers)
        return data

    def get_device_apps(self, deviceID):
        """
        Returns all the apps connected to a specific device.

        :param deviceID: the device UID
        :type deviceID: string
        :rtype: a list of dicts with information about apps
        """

        # https://api.relayr.io/devices/<deviceID>/apps
        url = '{0}/devices/{1}/apps'.format(self.host, deviceID)
        _, data = self.perform_request('GET', url, headers=self.headers)
        return data

    ## TODO: remove in version 0.3.0
    def post_devices_supscription(self, deviceID):
        """
        Deprecated method, replaced by ``post_devices_public_subscription``.

        This will be removed in version 0.3.0.
        """
        if config.LOG:
            self.logger.info("Deprecated method 'post_devices_supscription' called. Please use 'post_devices_public_subscription' instead.")
        self.post_devices_public_subscription(deviceID)

    def post_devices_public_subscription(self, deviceID):
        """
        Subscribes a user to a public device.

        :param deviceID: the device's UID
        :type deviceID: string
        :rtype: dict with connection credentials

        Sample result (anonymized values)::

            {
                "authKey": "...",
                "cipherKey": "...",
                "channel": "...",
                "subscribeKey": "sub-c-..."
            }
        """

        # https://api.relayr.io/devices/%s/subscription
        url = '{0}/devices/{1}/subscription'.format(self.host, deviceID)
        _, data = self.perform_request('POST', url, headers=self.headers)
        return data

    def post_devices_subscription(self, appID, deviceID):
        """
        Subscribes a user to a device.
        Sample result (anonymized values)::

            {
                "authKey": "...",
                "cipherKey": "...",
                "channel": "...",
                "subscribeKey": "sub-c-..."
            }
        """

        # https://api.relayr.io/apps/%s/devices/%s/subscription
        url = '{0}/apps/{1}/devices/{2}/subscription'.format(self.host, appID, deviceID)
        _, data = self.perform_request('POST', url, headers=self.headers)
        return data

    def post_device_command(self, deviceID, command, data):
        """
        Sends a command to a specific device.
        """
        # https://api.relayr.io/devices/<deviceID>/cmd/<command>
        url = '{0}/devices/{1}/cmd/{2}'.format(self.host, deviceID, command)
        _, data = self.perform_request('POST', url, data=data, headers=self.headers)
        return data

    def post_device_data(self, device_id, data):
        """
        Sends device JSON formatted data for a device (eg. temperature readings).
        """
        # https://api.relayr.io/devices/<device_id>/data
        url = '{0}/devices/{1}/data'.format(self.host, device_id)
        _, data = self.perform_request('POST', url, data=data, headers=self.headers)
        return data

    def post_device_app(self, deviceID, appID):
        """
        Connects a device to an app.

        Credentials for data reception are returned as part of the response.
        """
        # {{relayrAPI}}/devices/{{deviceID}}/apps/{{appID}}
        url = '{0}/devices/{1}/apps/{2}'.format(self.host, deviceID, appID)
        _, data = self.perform_request('POST', url, headers=self.headers)
        return data

    def delete_device_app(self, deviceID, appID):
        """
        Disconnects a device from an app.
        """
        # {{relayrAPI}}/devices/{{deviceID}}/apps/{{appID}}
        url = '{0}/devices/{1}/apps/{2}'.format(self.host, appID, deviceID)
        _, data = self.perform_request('DELETE', url, headers=self.headers)
        return data

    # ..............................................................................
    # Device models
    # ..............................................................................

    def get_public_device_models(self):
        """
        Returns list of all device models available on the relayr platform.

        :rtype: list of dicts, each representing a relayr device model
        """

        # https://api.relayr.io/device-models
        url = '{0}/device-models'.format(self.host)
        _, data = self.perform_request('GET', url)
        return data

    def get_device_model(self, devicemodelID):
        """
        Returns information about a specific device model.

        :rtype: A nested dictionary structure with fields describing the DM.
        """

        # https://api.relayr.io/device-models/<id>
        url = '{0}/device-models/{1}'.format(self.host, devicemodelID)
        _, data = self.perform_request('GET', url, headers=self.headers)
        return data

    def get_public_device_model_meanings(self):
        """
        Returns list of all device model meanings (no credentials needed).

        :rtype: list of dicts, each representing a relayr device model meaning
        """

        # https://api.relayr.io/device-models/meanings
        url = '{0}/device-models/meanings'.format(self.host)
        _, data = self.perform_request('GET', url)
        return data

    # ..............................................................................
    # Transmitters
    # ..............................................................................

    def get_transmitter(self, transmitterID):
        """
        Returns information about a specific transmitter with the given ID.

        :param transmitterID: the transmitter UID
        :type transmitterID: string
        :rtype: a dict with fields describing the transmitter
        """

        # https://api.relayr.io/transmitters/<id>
        url = '{0}/transmitters/{1}'.format(self.host, transmitterID)
        _, data = self.perform_request('GET', url, headers=self.headers)
        return data

    def post_transmitter(self, transmitterID, owner=None, name=None):
        """
        Registers a new Transmitter on the relayr platform.

        :param transmitterID: the transmitter UID
        :type transmitterID: string
        :param owner: the transmitters owner's UID
        :type owner: string
        :param name: the transmitter name
        :type name: string
        :rtype: an empty dict(?)
        """

        data = {}
        if owner is not None:
            data.update(owner=owner)
        if name is not None:
            data.update(name=name)

        # https://api.relayr.io/transmitters/<id>
        url = '{0}/transmitters/{1}'.format(self.host, transmitterID)
        _, data = self.perform_request('POST', url, data=data, headers=self.headers)
        return data

    def patch_transmitter(self, transmitterID, name=None):
        """
        Updates information about a specific transmitter.

        :param transmitterID: the transmitter UID
        :type transmitterID: string
        :param name: the transmitter name
        :type name: string
        :rtype: an empty dict(?)
        """

        data = {}
        if name is not None:
            data.update(name=name)

        # https://api.relayr.io/transmitters/<id>
        url = '{0}/transmitters/{1}'.format(self.host, transmitterID)
        _, data = self.perform_request('PATCH', url, data=data, headers=self.headers)
        return data

    def delete_transmitter(self, transmitterID):
        """
        Deletes a specific transmitter from the relayr platform.

        :param transmitterID: the transmitter UID
        :type transmitterID: string
        :rtype: an empty dict(?)
        """

        # https://api.relayr.io/transmitters/<id>
        url = '{0}/transmitters/{1}'.format(self.host, transmitterID)
        _, data = self.perform_request('DELETE', url, headers=self.headers)
        return data

    def post_transmitter_device(self, transmitterID, deviceID):
        """
        Connects a transmitter to a device.

        :param transmitterID: the transmitter UID
        :type transmitterID: string
        :param deviceID: the device UID
        :type deviceID: string
        :rtype: an empty dict(?)
        """

        # https://api.relayr.io/transmitters/<transmitterID>/devices/<deviceID>
        url = '{0}/transmitters/{1}/devices/{2}'.format(self.host, transmitterID, deviceID)
        _, data = self.perform_request('POST', url, headers=self.headers)
        return data

    def get_transmitter_devices(self, transmitterID):
        """
        Returns a list of devices connected to a specific transmitter.

        :param transmitterID: the transmitter UID
        :type transmitterID: string
        :rtype: a list of devices
        """

        # https://api.relayr.io/transmitters/<transmitterID>/devices
        url = '{0}/transmitters/{1}/devices'.format(self.host, transmitterID)
        _, data = self.perform_request('GET', url, headers=self.headers)
        return data

    def delete_transmitter_device(self, transmitterID, deviceID):
        """
        Disconnects a transmitter from a device.

        :param transmitterID: the transmitter UID
        :type transmitterID: string
        :param deviceID: the device UID
        :type deviceID: string
        :rtype: an empty dict(?)
        """

        # https://api.relayr.io/transmitters/<transmitterID>/devices/<deviceID>
        url = '{0}/transmitters/{1}/devices/{2}'.format(self.host, transmitterID, deviceID)
        _, data = self.perform_request('DELETE', url, data=data, headers=self.headers)
        return data
