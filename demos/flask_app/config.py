# config.py

from relayr_provider import Relayr


CONFIG = {    
    'rl': { # internal provider name
           
        # provider class
        'class_': Relayr,
        
        # relayr is an AuthorizationProvider so we need to set several other properties too:
        'consumer_key': '',
        'consumer_secret': '',
        'redirect_uri': 'https://relayr.io',

        # and it is also an OAuth 2.0 provider and it needs scope.
        'scope': ['access-own-user-info'],
    }
}
