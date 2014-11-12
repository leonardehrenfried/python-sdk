# -*- coding: utf-8 -*-

"""
This module contains exceptions raised when an operation on the 
relayr API or the relayr platform fails due to, 
for example: missing credentials, invalid UIDs, etc.

At the moment two exception classes are provided: 

- ``RelayrApiException``: raised for exceptions caused by API calls
- ``RelayrException``: raised for other exceptions
"""


class RelayrApiException(Exception):
    """
    RelayrApiException
    """

class RelayrException(Exception):
    """
    RelayrException
    """
