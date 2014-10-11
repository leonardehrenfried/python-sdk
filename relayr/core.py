# -*- coding: utf-8 -*-

"""
Low-level functionality of the Python bindings for the Relayr RESTful API.

The functions in this module map to the Relayr API endpoints and provide 
an internal layer for directly accessing the API itself. They are not really
intended for developers, who should rather work with the higher-level Relayr
abstractions provided b classes like ``App``, ``Device`` etc.

All these functions return the JSON response as returned by the Relayr API
interpreted as a Python datastructure with dicts, lists, strings, numbers
and None.

:copyright: Copyright 2014 by the relayr.io team, see AUTHORS.
:license: MIT, see LICENSE for details.
"""


import json

from jinja2 import Template
import requests

from relayr import exceptions, config


relayrAPI = config.relayrAPI


def return_result(resp):
    """
    Return the datastructure for the JSON result of an API call.
    
    Raise ``exceptions.RelayrApiException`` if the API causes an error.
    """

    if resp.status_code in [200, 201]:
        return resp.json()
    else:
        # msg = "%s - Called: PATCH %s" % (resp.json()['message'], url)
        msg = resp.json()['message']
        raise exceptions.RelayrApiException(msg)


# ..............................................................................
# Cloud
# ..............................................................................

# check email
def validate_email(userEmail):
    """
    Validate an user email address.
    
    :param userEmail: the user email address to be validated
    :type userEmail: string
    :rtype: A dict with certain fields describing the validation result.

    Sample result::

        {
            "exists": True
        }
    """
    
    # curl https://api.relayr.io/users/validate?email=<userEmail>
    
    template = Template('{{relayrAPI}}/users/validate?email={{userEmail}}')
    url = template.render(relayrAPI=relayrAPI, userEmail=userEmail)
    resp = requests.get(url)
    resp.connection.close()

    return return_result(resp)


def server_status():
    """
    Check server status.

    :rtype: A dict with certain fields describing the server status.

    Sample result::

        {
            "database": "ok"
        }
    """

    # curl https://api.relayr.io/server-status

    template = Template('{{relayrAPI}}/server-status')
    url = template.render(relayrAPI=relayrAPI)
    resp = requests.get(url)
    resp.connection.close()

    return return_result(resp)


def server_token(appID, **context):
    """
    Get the token representing a developer and a specific Relayr Application.
    
    :param appID: the application's UID
    :type appID: string

    :rtype: A dictionary with fields describing the token.

    Sample result (anonymized token value)::

        {
            "token": "1111111111-22222222222222_333333",
            "expiryDate": "2014-10-08T10:14:07.789Z"
        }
    """

    template = Template("{{relayrAPI}}/oauth2/appdev-token/%s" % appID)
    url = template.render(context)
    
    headers = {
        # 'User-Agent': '{{useragent}}',
        'Authorization': '{{token}}',
        'Content-Type': 'application/json'
    }
    template = Template(json.dumps(headers))
    headers = json.loads(template.render(context))
    
    resp = requests.get(url, headers=headers)
    resp.connection.close()
    
    return return_result(resp)


def server_replace_token(appID):
    """
    Generate a new token representing a developer and a Relayr Application.
    
    :param appID: the application's UID
    :type appID: string
    """

    raise NotImplementedError


def server_revoke_token(appID):
    """
    Revoke token
    """
    
    # {{relayrAPI}}/oauth2/appdev-token/{{appID}}
    raise NotImplementedError


# ..............................................................................
# Users
# ..............................................................................

# check user properties
def user_info(**context):
    """
    Return information about the user initiating the request.
    
    :rtype: A dictionary with fields describing the user.

    Sample result (anonymized token value)::
    
        {
            "email": "joe@foo.com", 
            "id": "11111111-2222-3333-4444-555555555555",
            "name": "joefoo"
        }
    """

    # cURL equivalent
    # curl https://api.relayr.io/oauth2/user-info
    
    template = Template('{{relayrAPI}}/oauth2/user-info')
    url = template.render(context)
    
    headers = {
        # 'User-Agent': '{{useragent}}',
        'Authorization': '{{token}}',
    }
    template = Template(json.dumps(headers))
    headers = json.loads(template.render(context))
    
    resp = requests.get(url, headers=headers)
    resp.connection.close()

    return return_result(resp)


def user_update_info(userID, name=None, email=None, **context):
    """
    Update one or more user attributes.
    
    :param userID: the uers's UID
    :type userID: string
    :param name: the user name to be set
    :type name: string
    :param email: the user email to be set
    :type email: string
    :rtype: ``True``, if successful, ``False`` otherwise
    """

    # cURL equivalent
    # curl PATCH https://api.relayr.io/users/<userId>

    template = Template("{{relayrAPI}}/users/%s" % userID)
    url = template.render(context)
    
    data = {}
    if name is not None:
        data.update(name=name)
    if email is not None:
        data.update(email=email)
    data = json.dumps(data)
    
    headers = {
        # 'User-Agent': '{{useragent}}',
        'Authorization': '{{token}}',
        'Content-Type': 'application/json',
        'clientId': '{{clientID}}',
        'clientSecret': '{{clientSecret}}',
        'response_type': '{{response_type}}',
        'scope': '{{scope}}',
    }
    template = Template(json.dumps(headers))
    headers = json.loads(template.render(context))
    
    resp = requests.patch(url, data=data, headers=headers)
    resp.connection.close()

    return return_result(resp)


def user_publishers(userID, **context):
    """
    Return all publishers owned by a specific user.

    :param userID: the uers's UID
    :type userID: string
    :rtype: list of dicts ... 
    """

    template = Template("{{relayrAPI}}/users/%s/publishers" % userID)
    url = template.render(relayrAPI=relayrAPI)

    headers = {
        # 'User-Agent': '{{useragent}}',
        'Authorization': '{{token}}',
    }
    template = Template(json.dumps(headers))
    headers = json.loads(template.render(context))
        
    resp = requests.get(url, headers=headers)
    resp.connection.close()
    
    return return_result(resp)


def user_apps(userID, **context):
    """
    Returns all apps installed for a specific user.

    :param userID: the uers's UID
    :type userID: string
    :rtype: list of dicts ... with IDs and secrets
    """

    template = Template("{{relayrAPI}}/users/%s/apps" % userID)
    url = template.render(relayrAPI=relayrAPI)

    headers = {
        # 'User-Agent': '{{useragent}}',
        'Authorization': '{{token}}',
    }
    template = Template(json.dumps(headers))
    headers = json.loads(template.render(context))
        
    resp = requests.get(url, headers=headers)
    resp.connection.close()
    
    return return_result(resp)


def user_transmitters(userID):
    """
    Return all transmitters under a specific user.

    :param userID: the uers's UID
    :type userID: string
    :rtype: list of dicts with IDs and secrets
    """

    template = Template("{{relayrAPI}}/users/%s/transmitters" % userID)
    url = template.render(relayrAPI=relayrAPI)

    template = Template(json.dumps(headers))
    headers = json.loads(template.render(testset1))
    
    resp = requests.post(url) # ???
    resp.connection.close()
    
    return return_result(resp)


def user_devices(userID, **context):
    """
    Returns all devices registered for a specific user.

    :param userID: the uers's UID
    :type userID: string
    :rtype: list of dicts ...
    """

    template = Template("{{relayrAPI}}/users/%s/devices" % userID)
    url = template.render(relayrAPI=relayrAPI)

    headers = {
        # 'User-Agent': '{{useragent}}',
        'Authorization': '{{token}}',
    }
    template = Template(json.dumps(headers))
    headers = json.loads(template.render(context))
        
    resp = requests.get(url, headers=headers)
    resp.connection.close()
    
    return return_result(resp)


def user_connect_public_device(deviceID, callback, **context):
    """
    Subscribe an user to a public device.

    :param deviceID: the device's UID
    :type deviceID: string
    :rtype: list of dicts ...
    
    Sample result (anonymized values)::

        {
            "authKey": "11111111-2222-3333-4444-555555555555", 
            "cipherKey": "1212121212121212121212121212121212121212121212121212121212121212", 
            "channel": "40779093-0be0-4c13-b1b1-e2568548b5c7:8a658df8-df55-4314-a913-9a5d45395f64", 
            "channel": "22222222-3333-4444-5555-666666666666:33333333-4444-5555-6666-777777777777", 
            "subscribeKey": "sub-c-44444444-5555-6666-7777-888888888888"
        }
    """

    template = Template("{{relayrAPI}}/devices/%s/subscription" % deviceID)
    url = template.render(relayrAPI=relayrAPI)

    headers = {
        # 'User-Agent': '{{useragent}}',
        'Authorization': '{{token}}',
    }
    template = Template(json.dumps(headers))
    headers = json.loads(template.render(context))
        
    resp = requests.post(url, headers=headers)
    res = resp.json()
    resp.connection.close()
    
    if 0:
        from Pubnub import Pubnub
        pubnub = Pubnub(
            None, # publish key
            res['subscribeKey'],
            cipher_key=res['cipherKey'],
            auth_key=res['authKey'],
            secret_key=None,
            ssl_on=False
        )
        pubnub.subscribe(res['channel'], callback)

    from config import dataConnectionHubName
    if dataConnectionHubName == 'PubNub':
        from dataconnection import PubnubDataConnection as Connection
        conn = Connection(**res)
        conn.subscribe(res['channel'], callback)


def user_wunderbar(userID, **context):
    """
    Return the IDs and Secrets of the Master Module and Sensor Modules.

    :param userID: the users's UID
    :type userID: string
    :rtype: dict with information about master and sensor modules/devices
    
    Sample result (some values anonymized)::

        {
            "bridge": {
                "name": "My Wunderbar Bridge Module", 
                "public": False, 
                "secret": "......", 
                "owner": "...", 
                "model": {
                    "readings": [], 
                    "manufacturer": "Relayr GmbH", 
                    "id": "...", 
                    "name": "Wunderbar Bridge Module"
                }, 
                "id": "1080a278-faf2-44df-96ab-bfd22e466547", 
                "firmwareVersion": "1.0.0"
            }, 
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
            "light": {
                "name": "My Wunderbar Light & Proximity Sensor", 
                "public": False, 
                "secret": "......", 
                "owner": "...", 
                "model": {
                    "readings": [
                        {
                            "meaning": "proximity", 
                            "unit": "number"
                        }, 
                        {
                            "meaning": "color", 
                            "unit": "rgb"
                        }, 
                        {
                            "meaning": "luminosity", 
                            "unit": "lumen"
                        }
                    ], 
                    "manufacturer": "Relayr GmbH", 
                    "id": "...", 
                    "name": "Wunderbar Light & Proximity Sensor"
                }, 
                "id": "...", 
                "firmwareVersion": "1.0.0"
            }, 
            "masterModule": {
                "owner": "...", 
                "secret": "............", 
                "id": "...", 
                "name": "My Wunderbar Master Module"
            }, 
            "infrared": {
                "name": "My Wunderbar Infrared Sensor ", 
                "public": False, 
                "secret": "......", 
                "owner": "...", 
                "model": {
                    "readings": [], 
                    "manufacturer": "Relayr GmbH", 
                    "id": "...", 
                    "name": "Wunderbar Infrared Sensor"
                }, 
                "id": "...", 
                "firmwareVersion": "1.0.0"
            }, 
            "thermometer": {
                "name": "My Wunderbar Thermometer & Humidity Sensor", 
                "public": False, 
                "secret": "......", 
                "owner": "...", 
                "model": {
                    "readings": [
                        {
                            "meaning": "temperature", 
                            "minimum": -100.0, 
                            "maximum": 100.0, 
                            "unit": "celsius", 
                            "precision": 0.25
                        }, 
                        {
                            "meaning": "humidity", 
                            "unit": "percent"
                        }
                    ], 
                    "manufacturer": "Relayr GmbH", 
                    "id": "...", 
                    "name": "Wunderbar Thermometer & Humidity Sensor"
                }, 
                "id": "...", 
                "firmwareVersion": "1.0.0"
            }, 
            "gyroscope": {
                "name": "My Wunderbar Accelerometer & Gyroscope", 
                "public": False, 
                "secret": "......", 
                "owner": "...", 
                "model": {
                    "readings": [
                        {
                            "meaning": "angular_speed", 
                            "unit": "degrees_per_second"
                        }, 
                        {
                            "meaning": "acceleration", 
                            "unit": "g"
                        }
                    ], 
                    "manufacturer": "Relayr GmbH", 
                    "id": "...", 
                    "name": "Wunderbar Accelerometer & Gyroscope"
                }, 
                "id": "...", 
                "firmwareVersion": "1.0.0"
            }
        }    
    """

    template = Template("{{relayrAPI}}/users/%s/wunderbar" % userID)
    url = template.render(relayrAPI=relayrAPI)

    headers = {
        # 'User-Agent': '{{useragent}}',
        'Authorization': '{{token}}',
    }
    
    template = Template(json.dumps(headers))
    headers = json.loads(template.render(token=context['token']))
    
    # print(url)
    # print(headers)
    
    resp = requests.post(url, headers=headers)
    resp.connection.close()

    return return_result(resp)


def user_wunderbar_remove_all(userID, **context):
    """
    Remove all Wunderbars associated with a specific user.

    :param userID: the users's UID
    :type userID: string
    """

    template = Template("{{relayrAPI}}/users/%s/destroy-everything-i-love" % userID)
    url = template.render(relayrAPI=relayrAPI)

    headers = {
        # 'User-Agent': '{{useragent}}',
        'Authorization': '{{token}}',
    }
    
    template = Template(json.dumps(headers))
    headers = json.loads(template.render(token=context['token']))
    
    resp = requests.post(url, headers=headers)
    resp.connection.close()

    return return_result(resp)


# ..............................................................................
# Publishers endpoints
# ..............................................................................

def list_all_publishers():
    """
    Return list of all publishers (no credentials needed).

    :rtype: list of dicts, each representing a relayr publisher
    """

    template = Template('{{relayrAPI}}/publishers')
    url = template.render(relayrAPI=relayrAPI)
    resp = requests.get(url)
    resp.connection.close()

    return return_result(resp)


def publisher_register(userID, name, **context):
    """
    Register a new publisher.

    :param userID: the user UID of the publisher
    :type userID: string
    :param name: the publisher name
    :type name: string
    :rtype: a dict with fields describing the new publisher
    """

    template = Template("{{relayrAPI}}/publishers")
    url = template.render(relayrAPI=relayrAPI)
    
    headers = {
        # 'User-Agent': '{{useragent}}',
        'Authorization': '{{token}}',
        'Content-Type': 'application/json'
    }
    template = Template(json.dumps(headers))
    headers = json.loads(template.render(token=context['token']))

    data = {'owner': userID, 'name': name}

    resp = requests.post(url, headers=headers, data=data)
    resp.connection.close()
    
    return return_result(resp)


def publisher_delete(publisherID, **context):
    """
    Delete a specific publisher from the Relayr cloud.

    :param publisherID: the publisher UID
    :type publisherID: string
    :rtype: an empty dict(?)
    """

    template = Template("{{relayrAPI}}/publishers/{{publisherID}}")
    url = template.render(relayrAPI=relayrAPI, publisherID=publisherID)
    
    headers = {
        # 'User-Agent': '{{useragent}}',
        'Authorization': '{{token}}',
    }
    template = Template(json.dumps(headers))
    headers = json.loads(template.render(token=context['token']))
    
    resp = requests.delete(url, headers=headers)
    resp.connection.close()
    
    return return_result(resp)


# get publisher apps
def publisher_apps(publisherID, **context):
    """
    Returns a list of apps published by a specific publisher.
    
    :rtype: A list of apps.
    """

    template = Template('{{relayrAPI}}/publishers/%s/apps' % publisherID)
    url = template.render(relayrAPI=relayrAPI)

    resp = requests.get(url)
    resp.connection.close()
    
    return return_result(resp)


# get publisher apps extended
def publisher_apps_extended(publisherID, **context):
    """
    Returns a list of extended apps published by a specific publisher.
    
    :rtype: A list of apps.
    """

    template = Template('{{relayrAPI}}/publishers/%s/apps/extended' % publisherID)
    url = template.render(relayrAPI=relayrAPI)

    resp = requests.get(url)
    resp.connection.close()
    
    return return_result(resp)


def publisher_update_info(publisherID, name=None, **context):
    """
    Update one or more publisher attributes.
    
    :param publisherID: the publisher's UID
    :type publisherID: string
    :param name: the publisher name to be set
    :type name: string
    :rtype: ``True``, if successful, ``False`` otherwise
    """

    # cURL equivalent
    # curl PATCH https://api.relayr.io/publishers/<publisherID>

    template = Template("{{relayrAPI}}/publishers/%s" % publisherID)
    url = template.render(context)
    
    data = {}
    if name is not None:
        data.update(name=name)
    data = json.dumps(data)
    
    headers = {
        # 'User-Agent': '{{useragent}}',
        'Authorization': '{{token}}',
        'Content-Type': 'application/json',
        'clientId': '{{clientID}}',
        'clientSecret': '{{clientSecret}}',
        'response_type': '{{response_type}}',
        'scope': '{{scope}}',
    }
    template = Template(json.dumps(headers))
    headers = json.loads(template.render(context))
    
    resp = requests.patch(url, data=data, headers=headers)
    resp.connection.close()

    return return_result(resp)


# ..............................................................................
# Application
# ..............................................................................

def list_all_apps():
    """
    Return list of all applications (no credentials needed).

    :rtype: list of dicts, each representing a relayr application
    """

    template = Template('{{relayrAPI}}/apps')
    url = template.render(relayrAPI=relayrAPI)
    resp = requests.get(url)
    resp.connection.close()

    return return_result(resp)


def app_get_sdk_info(appID, **context):
    """
    Return info about the app initiating the request (the one in the token).
    
    Sample result (anonymized token value)::
    
        {
            "id": "11111111-2222-3333-4444-555555555555",
            "name": "My App",
            "description": "My Wunderbar app"
        }
    """

    template = Template("{{relayrAPI}}/oauth2/app-info")
    url = template.render(relayrAPI=relayrAPI)
    
    headers = {
        # 'User-Agent': '{{useragent}}',
        'Authorization': '{{token}}',
    }
    template = Template(json.dumps(headers))
    headers = json.loads(template.render(context))

    resp = requests.get(url, headers=headers)
    resp.connection.close()
    
    return return_result(resp)


def app_get_info(appID, **context):
    """
    Returns information about the app with the given ID.
    
    Sample result (anonymized token value)::
    
        {
            "id": "11111111-2222-3333-4444-555555555555",
            "name": "My App",
            "description": "My Wunderbar app",
            ...
        }
    """

    template = Template("{{relayrAPI}}/apps/{{appID}}")
    url = template.render(relayrAPI=relayrAPI, appID=appID)
    
    resp = requests.get(url)
    resp.connection.close()
    
    return return_result(resp)


def app_get_info_extended(appID, **context):
    """
    Returns extended information about the app with the given ID.
    
    Sample result (some values anonymized)::
    
        {
            "id": "11111111-2222-3333-4444-555555555555",
            "name": "My App",
            "publisher": "22222222-3333-4444-5555-666666666666",
            "clientId": "cccccccccccccccccccccccccccccccc",
            "clientSecret": "ssssssssssssssssssssssssssssssss",
            "description": "My Wunderbar app",
            "redirectUri": https://relayr.io
        }
    """

    template = Template("{{relayrAPI}}/apps/{{appID}}/extended")
    url = template.render(relayrAPI=relayrAPI, appID=appID)
    
    resp = requests.get(url)
    resp.connection.close()
    
    return return_result(resp)


def app_patch(appID, description=None, name=None, redirectUri=None, **context):
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
            "id": "11111111-2222-3333-4444-555555555555",
            "name": "My App",
            "publisher": "22222222-3333-4444-5555-666666666666",
            "clientId": "cccccccccccccccccccccccccccccccc",
            "clientSecret": "ssssssssssssssssssssssssssssssss",
            "description": "My Wunderbar app",
            "redirectUri": https://relayr.io
        }
    """

    template = Template("{{relayrAPI}}/apps/{{appID}}")
    url = template.render(relayrAPI=relayrAPI, appID=appID)

    data = {}
    if name is not None:
        data.update(name=name)
    if description is not None:
        data.update(description=description)
    if redirectUri is not None:
        data.update(redirectUri=redirectUri)
    template = Template(json.dumps(data))
    data = template.render(context)
    
    headers = {
        'User-Agent': '{{useragent}}',
        'Authorization': '{{token}}',
        'Content-Type': 'application/json'
    }
    template = Template(json.dumps(headers))
    headers = json.loads(template.render(context))
    
    resp = requests.patch(url, data=data, headers=headers)
    resp.connection.close()
    
    return return_result(resp)


# ..............................................................................
# Devices
# ..............................................................................

def list_all_public_devices(meaning=''):
    """
    Return list of all public devices (no credentials needed).

    :param meaning: required meaning in the device model's ``readings`` attribute
    :type meaning: string
    :rtype: list of dicts, each representing a relayr device
    """

    path = '{{relayrAPI}}/devices/public'
    if meaning:
        path += '?meaning=%s' % meaning
    template = Template(path)
    url = template.render(relayrAPI=relayrAPI)
    resp = requests.get(url)
    resp.connection.close()

    return return_result(resp)


def device(deviceID, **context):
    """
    Return information about a specific device with given UID.
        
    :param deviceID: the device UID
    :type deviceID: string
    :rtype: a dict with fields containing information about the device

    Raises ``exceptions.RelayrApiException`` for invalid UIDs or missing 
    credentials...
    """
    
    # curl https://api.relayr.io/devices/<deviceID>/apps

    template = Template('{{relayrAPI}}/devices/%s' % deviceID)
    url = template.render(relayrAPI=relayrAPI)

    headers = {
        'Authorization': '{{token}}',
        'Content-Type': 'application/json'
    }
    template = Template(json.dumps(headers))
    headers = json.loads(template.render(context))
    
    resp = requests.get(url, headers=headers)
    resp.connection.close()

    return return_result(resp)


def device_apps(deviceID, **context):
    """
    Return all the apps connected to a specific device.

    :param deviceID: the device UID
    :type deviceID: string
    :rtype: a list of dicts with information about apps
    """

    template = Template('{{relayrAPI}}/devices/%s/apps' % deviceID)
    url = template.render(relayrAPI=relayrAPI)

    headers = {
        'Authorization': '{{token}}',
        'Content-Type': 'application/json'
    }
    template = Template(json.dumps(headers))
    headers = json.loads(template.render(context))
    
    resp = requests.get(url, headers=headers)
    resp.connection.close()

    return return_result(resp)


def device_command(deviceID, command, **context):
    """
    Send a command to a specific device.
    """

    template = Template('{{relayrAPI}}/devices/%s/cmd/%s' % (deviceID, command))
    url = template.render(relayrAPI=relayrAPI)

    headers = {
        'Authorization': '{{token}}',
        'Content-Type': 'application/json'
    }
    template = Template(json.dumps(headers))
    headers = json.loads(template.render(context))
    
    ## TODO: command in the POST data or the path?? 
    
    resp = requests.post(url, headers=headers)
    resp.connection.close()

    return return_result(resp)


# ..............................................................................
# Device models
# ..............................................................................

def list_all_device_models():
    """
    Return list of all device models (no credentials needed).

    :rtype: list of dicts, each representing a Relayr device model
    """

    template = Template('{{relayrAPI}}/device-models')
    url = template.render(relayrAPI=relayrAPI)
    resp = requests.get(url)
    resp.connection.close()

    return return_result(resp)


def list_all_device_model_meanings():
    """
    Return list of all device model meanings (no credentials needed).

    :rtype: list of dicts, each representing a Relayr device model meaning
    """

    template = Template('{{relayrAPI}}/device-models/meanings')
    url = template.render(relayrAPI=relayrAPI)
    resp = requests.get(url)
    resp.connection.close()

    return return_result(resp)


def devicemodel_info(id, **context):
    """
    Return information about a device model with a specific ID.
    
    :rtype: A nested dictionary structure with fields describing the DM.
    """

    template = Template('{{relayrAPI}}/device-models/%s' % id)
    url = template.render(relayrAPI=relayrAPI)
    
    resp = requests.get(url)
    resp.connection.close()

    return return_result(resp)


# ..............................................................................
# Transmitters
# ..............................................................................

def transmitter_get_info(transmitterID, **context):
    """
    Returns information about a specific transmitter with the given ID.

    :param transmitterID: the transmitter UID
    :type transmitterID: string
    :rtype: a dict with fields describing the transmitter
    """

    template = Template("{{relayrAPI}}/transmitters/{{transmitterID}}")
    url = template.render(relayrAPI=relayrAPI, transmitterID=transmitterID)
    
    headers = {
        # 'User-Agent': '{{useragent}}',
        'Authorization': '{{token}}',
    }
    template = Template(json.dumps(headers))
    headers = json.loads(template.render(token=context['token']))
    
    resp = requests.get(url, headers=headers)
    resp.connection.close()
    
    return return_result(resp)


def transmitter_set_info(transmitterID, name=None, **context):
    """
    Update information about a specific transmitter with the given ID.

    :param transmitterID: the transmitter UID
    :type transmitterID: string
    :param name: the transmitter name
    :type name: string
    :rtype: an empty dict(?)
    """

    template = Template("{{relayrAPI}}/transmitters/{{transmitterID}}")
    url = template.render(relayrAPI=relayrAPI, transmitterID=transmitterID)
    
    data = {}
    if name is not None:
        data.update(name=name)
    data = json.dumps(data)
    
    headers = {
        # 'User-Agent': '{{useragent}}',
        'Authorization': '{{token}}',
        'Content-Type': 'application/json'
    }
    template = Template(json.dumps(headers))
    headers = json.loads(template.render(token=context['token']))
    
    resp = requests.patch(url, data=data, headers=headers)
    resp.connection.close()
    
    return return_result(resp)


def transmitter_delete(transmitterID, **context):
    """
    Delete a specific transmitter from the Relayr cloud.

    :param transmitterID: the transmitter UID
    :type transmitterID: string
    :rtype: an empty dict(?)
    """

    template = Template("{{relayrAPI}}/transmitters/{{transmitterID}}")
    url = template.render(relayrAPI=relayrAPI, transmitterID=transmitterID)
    
    headers = {
        # 'User-Agent': '{{useragent}}',
        'Authorization': '{{token}}',
    }
    template = Template(json.dumps(headers))
    headers = json.loads(template.render(token=context['token']))
    
    resp = requests.delete(url, headers=headers)
    resp.connection.close()
    
    return return_result(resp)


def transmitter_register(userID, name, **context):
    """
    Register a new transmitter.

    :param userID: the user UID of the transmitter's owner
    :type userID: string
    :param name: the transmitter name
    :type name: string
    :rtype: a dict with fields describing the new transmitter
    """

    template = Template("{{relayrAPI}}/transmitters")
    url = template.render(relayrAPI=relayrAPI)
    
    headers = {
        # 'User-Agent': '{{useragent}}',
        'Authorization': '{{token}}',
        'Content-Type': 'application/json'
    }
    template = Template(json.dumps(headers))
    headers = json.loads(template.render(token=context['token']))

    data = {'owner': userID, 'name': name}

    resp = requests.post(url, headers=headers, data=data)
    resp.connection.close()
    
    return return_result(resp)


def transmitter_register_connection_device(transmitterID, deviceID, **context):
    """
    Connect a transmitter to a device.

    :param transmitterID: the transmitter UID
    :type transmitterID: string
    :param deviceID: the device UID
    :type deviceID: string
    :rtype: an empty dict(?)
    """

    template = Template("{{relayrAPI}}/transmitters/{{transmitterID}}/devices/{{deviceID}}")
    url = template.render(relayrAPI=relayrAPI, transmitterID=transmitterID, deviceID=deviceID)
    
    headers = {
        # 'User-Agent': '{{useragent}}',
        'Authorization': '{{token}}',
        'Content-Type': 'application/json'
    }
    template = Template(json.dumps(headers))
    headers = json.loads(template.render(token=context['token']))

    resp = requests.post(url, headers=headers)
    resp.connection.close()
    
    return return_result(resp)


def transmitter_get_devices(transmitterID, **context):
    """
    Return a list of devices connected to a specific transmitter.

    :param transmitterID: the transmitter UID
    :type transmitterID: string
    :rtype: a list of devices
    """

    template = Template("{{relayrAPI}}/transmitters/{{transmitterID}}/devices")
    url = template.render(relayrAPI=relayrAPI, transmitterID=transmitterID)
    
    headers = {
        # 'User-Agent': '{{useragent}}',
        'Authorization': '{{token}}',
    }
    template = Template(json.dumps(headers))
    headers = json.loads(template.render(token=context['token']))
    
    resp = requests.get(url, headers=headers)
    resp.connection.close()
    
    return return_result(resp)


def transmitter_delete_device_connection(transmitterID, deviceID, **context):
    """
    Delete a connection with a device.

    :param transmitterID: the transmitter UID
    :type transmitterID: string
    :param deviceID: the device UID
    :type deviceID: string
    :rtype: an empty dict(?)
    """

    template = Template("{{relayrAPI}}/transmitters/{{transmitterID}}/devices{{deviceID}}")
    url = template.render(relayrAPI=relayrAPI, transmitterID=transmitterID, deviceID=deviceID)
    
    headers = {
        # 'User-Agent': '{{useragent}}',
        'Authorization': '{{token}}',
    }
    template = Template(json.dumps(headers))
    headers = json.loads(template.render(token=context['token']))
    
    resp = requests.delete(url, headers=headers)
    resp.connection.close()
    
    return return_result(resp)
