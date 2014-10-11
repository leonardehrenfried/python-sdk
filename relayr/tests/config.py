# A set of variables used for testing the relayr API.
# Attention: You must provide your own eaningful values 
# before you can run large parts of the test suite!

# Get 'token' on relayr.io and prefix with 'Bearer '!

testset0 = {
    'userEmail': 'god@in.heaven',
    'relayrAPI': 'https://api.relayr.io',
    'redirectURI': 'https://relayr.io'
}

testset1 = {
    'userID': '...', 
    'userName': '...', 
    'userEmail': '...',
    'relayrAPI': 'https://api.relayr.io',
    'redirectURI': 'https://relayr.io',
    'response_type': 'code',
    'clientId': '...',
    'clientSecret': '...',
    'scope': '...',
    'appID': '...',
    'appName': '...',
    'publisherID': '...',
    'deviceID': '...',
    'description': "...",
    'useragent': '...',
    'token': 'Bearer ...'
}

testset2 = {
    'publisherID': '...',
}

testset3 = {
    'PUBLISH_KEY': 'pub-c-...',
    'SUBSCRIBE_KEY': 'sub-c-...',
    'channel': 'test-channel',
    'message': 'hi there 11'
}

testset4 = {
    'bluetoothAddr': '...',
}
