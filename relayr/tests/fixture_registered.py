"""
A set of variables used for testing the relayr API.
Attention: You must provide your own eaningful values 
before you can run large parts of the test suite!

Get 'token' on relayr.io!

Remember that tokens expire after some time, check the documentation!
"""

testset1 = {
    'userID': '...', 
    'userName': '...', 
    'userEmail': '...',
    'relayrAPI': 'https://api.relayr.io',
    'redirectURI': 'https://relayr.io',
    'response_type': 'code',
    'clientId': '...',
    'clientSecret': '...',
    'scope': 'access-own-user-info',
    'appID': '...',
    'appName': '...',
    'publisherID': '...',
    'deviceID': '...',
    'description': "...",
    'useragent': '...',
    'token': '...',
}

special = {
    'token': '...',
    'userName': '...', 
    'publisherID': '...',
    'deviceID': '...',
    'transmitterID': '...',
}

testset2 = {
    'publisherID': '...',
}

testset3 = {
    'PUBLISH_KEY': '...',
    'SUBSCRIBE_KEY': '...',
    'channel': '...',
    'message': '...'
}

testset4 = {
    'bluetoothAddr': '...',
}
