# -*- coding: utf-8 -*-

"""
Relayr cloud/server abstractions.
"""


from relayr import core


def validate_email(userEmail):
    """
    Validate an user email address.
    
    :param userEmail: the user email address to be validated
    :type userEmail: string
    :rtype: ``True``, if the given email address is already registered, 
        ``False`` otherwise.
    """
    res = core.validate_email(userEmail)
    return res['exists'] == True


def server_status():
    """
    Check server status.

    :rtype: A Boolean, ``True``, if the server is alive and kicking, 
        ``False`` otherwise.
    """
    res = core.server_status()
    return res['database'] == 'ok'
