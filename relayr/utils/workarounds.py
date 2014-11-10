#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Workaround functions and stuff...
"""

import json


def cleanup_pubnub_message_py3(message):
    """
    Return a cleaned version of a PubNub message under Python 3.

    Workaround for Pubnub in Python 3 passing messages appended with
    strange characters ('\x06', '\x07') plus outer quotes... making json
    barf.

    PY3: '"{\\"ts\\":1414672791632,\\"snd_level\\":25}"\x07\x07\x07\x07\x07\x07\x07'
    PY2: '\'{"ts":1414672791632,"snd_level":25}\''
    """
    low_ascii_chars = ''.join([chr(i) for i in range(8)])
    res = message.rstrip(low_ascii_chars)
    res = json.loads(res)

    return res
