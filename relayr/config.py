# -*- coding: utf-8 -*-

"""
A set of configuration variables used for various purposes.

This module provides defaults for configuration variables and a way
of overwriting these from the shell environment or a script using
the Relayr Client.
"""

import os
import platform

from .version import __version__


# defaults
relayrAPI = 'https://api.relayr.io'
clientName = 'python-sdk'
dataConnectionHubName = 'PubNub'
userAgentString = '{client_name}/{client_version} ({platform}; {python_implementation} {python_version})'
DEBUG = False
LOG = False
LOG_DIR = os.getcwd()

# overwrite with environment variables if given
relayrAPI = os.environ.get('RELAYR_API', relayrAPI)
clientName = os.environ.get('RELAYR_PYTHON_CLIENT_NAME', clientName)
dataConnectionHubName = os.environ.get('RELAYR_DATAHUB', dataConnectionHubName)
userAgentString = os.environ.get('RELAYR_DATAHUB', userAgentString)
DEBUG = True if os.environ.get('RELAYR_DEBUG', 'False') == 'True' else False
LOG = True if os.environ.get('RELAYR_LOG', 'False') == 'True' else False
LOG_DIR = os.environ.get('RELAYR_LOG_DIR', LOG_DIR)

# derived variable, HTTP user-agent string
userAgent = userAgentString.format(
	client_name=clientName,
	client_version=__version__,
	platform=platform.platform(),
	python_implementation=platform.python_implementation(),
	python_version=platform.python_version(),
)

del os, platform
