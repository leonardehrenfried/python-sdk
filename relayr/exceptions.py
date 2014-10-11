# -*- coding: utf-8 -*-

"""
This module contains exceptions raised when certain operations on the 
Relayr API fail, like missing credentials, invalid UIDs, etc.

Right now two exception classes are provided: 

- ``RelayrApiException`` is raised for exceptions caused by API calls
- ``RelayrException`` is raised for other exceptions

:copyright: Copyright 2014 by the relayr.io team, see AUTHORS.
:license: MIT, see LICENSE for details.
"""


class RelayrApiException(Exception):
    """
    RelayrApiException
    """

class RelayrException(Exception):
    """
    RelayrException
    """
