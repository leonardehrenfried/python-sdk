# -*- coding: utf-8 -*-

"""
A set of configuration variables which the user should rarely care about.
"""

import platform

from .version import __version__


relayrAPI = 'https://api.relayr.io'
dataConnectionHubName = 'PubNub' # Soon MQTT...?
userAgent = 'Python-Relayr-Client/{version} ({plat}; {pyimpl} {pyver})'.format(
	version=__version__,
	plat=platform.platform(),
	pyimpl=platform.python_implementation(),
	pyver=platform.python_version(),
)

del platform
