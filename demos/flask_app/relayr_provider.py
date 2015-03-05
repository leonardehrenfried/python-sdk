import json

import authomatic.core as core
from authomatic.providers.oauth2 import OAuth2, PROVIDER_ID_MAP

from relayr import Client


class Relayr(OAuth2):
    """
    Relayr |oauth2| provider.
    
    .. warning::
        |no-csrf|

    * Dashboard: https://developer.relayr.io
    * Docs: https://developer.relayr.io/documents/Welcome/Introduction
    * Public API reference: https://developer.relayr.io/documents/relayrAPI/Introduction

    Supported :class:`.User` properties:

    * name
    * id
    * email
    """

    # https://developer.relayr.io/documents/Welcome/OAuthReference

    supported_user_attributes = core.SupportedUserAttributes(
        name=True,
        id=True,
        email=True
    )
    
    supports_csrf_protection = False
    _x_use_authorization_header = False

    user_authorization_url = 'https://api.relayr.io/oauth2/auth'
    access_token_url = 'https://api.relayr.io/oauth2/token'
    user_info_url = 'https://api.relayr.io/oauth2/user-info'
    user_info_scope = ['access-own-user-info']

    def __init__(self, *args, **kwargs):
        super(Relayr, self).__init__(*args, **kwargs)
        
        if self.offline:
            if not 'grant_type' in self.access_token_params:
                self.access_token_params['grant_type'] = 'refresh_token'
    
    def _x_scope_parser(self, scope):
        # relayr has space-separated scopes
        return ' '.join(scope)

    @staticmethod
    def _x_user_parser(user, data):
        client = Client(token=user.credentials.token)
        usr = client.get_user()
        user.name = usr.name
        user.id = usr.id
        user.email = usr.email
        user.transmitters = list(usr.get_transmitters())        
        user.transmitters_devices = {}
        for t in user.transmitters:
            user.transmitters_devices[t.name] = client.api.get_transmitter_devices(t.id)
        return user


PROVIDER_ID_MAP.append(Relayr)
