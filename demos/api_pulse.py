#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Show current Relayr API key figures on the command-line.

This script uses the Python bindings for the Relayr RESTful API as defined
in the ``relayr`` Python package. It should work as-is on Python 2 and 3.

Example:

$ python api_pulse.py 
Relayr API Pulse
............................................................................
Path: demos/api_pulse.py
MD5 hash: 339bafd0a28b18beed54ea5a90f5710d
API: https://api.relayr.io
Python Relayr client version: 0.2.2
Python version: CPython 2.7.8
Platform: Darwin-14.0.0-x86_64-i386-64bit
Date/Time: 2014-12-23T11:08:17.754622
............................................................................
server status ok: True (1.02 s)
317 publishers (0.64 s)
199 applications (0.74 s)
109 public devices (0.87 s)
8 device models (0.42 s)
8 device model meanings (0.47 s)
#public devices by meaning: {
    "acceleration": 17,
    "temperature": 33,
    "noise_level": 18,
    "angular_speed": 17,
    "color": 28,
    "luminosity": 28,
    "proximity": 28,
    "humidity": 33
}
"""

import sys
import json
import time
import datetime
import platform
from hashlib import md5

import termcolor

from relayr import Api
from relayr.compat import urlopen, URLError
from relayr.version import __version__ as relayr_version
from relayr.utils.terminalsize import get_terminal_size


def connected_to_internet():
    "Check if we have access to 'the internet', well some Google server."

    try:
        # Give IP address to avoid potential DNS issues.
        response = urlopen('http://74.125.228.100')
        return True
    except URLError as err:
        return False


def show_versions():
    "Show some versioning info."
    
    # Show header lines.
    api = Api()
    url = api.host
    dt = datetime.datetime.now().isoformat()
    term_width = get_terminal_size()[0]
    print('.' * term_width)
    print('Path: %s' % __file__)
    hash = md5(open(__file__).read().encode('utf8')).hexdigest()
    print('MD5 hash: %s' % hash)
    print('API: %s' % url)
    print('Python Relayr client version: %s' % relayr_version)
    pyimpl = platform.python_implementation()
    pyver = platform.python_version()
    platf = platform.platform()
    print('Python version: %s %s' % (pyimpl, pyver))
    print('Platform: %s' % platf)
    print('Date/Time: %s' % dt)
    print('.' * term_width)
    

def show_check():
    "Show some key numbers about the current state of the API."
    
    # For all this no credentials/token etc. are needed.
    api = Api()

    # Get server status.
    t0 = time.time()
    try:
        res = api.get_server_status()
        ok = res['database'] == 'ok'
    except:
        msg = 'Relayr API not reachable, sorry for that!'
        termcolor.cprint(msg, 'red')
        sys.exit(-1)
    t = time.time() - t0
    print('server status ok: %s (%.2f s)' % (ok, t))

    # Get number of all publishers.
    t0 = time.time()
    publishers = list(api.get_public_publishers())
    t = time.time() - t0
    print('%d publishers (%.2f s)' % (len(publishers), t))

    # Get number of all apps.
    t0 = time.time()
    apps = list(api.get_public_apps())
    t = time.time() - t0
    print('%d applications (%.2f s)' % (len(apps), t))
    
    # Get number of all public devices.
    t0 = time.time()
    devices = list(api.get_public_devices())
    t = time.time() - t0
    print('%d public devices (%.2f s)' % (len(devices), t))

    # Get number of all device models.
    t0 = time.time()
    models = list(api.get_public_device_models())
    t = time.time() - t0
    print('%d device models (%.2f s)' % (len(models), t))

    # Get number of all device model meanings.
    t0 = time.time()
    meanings = list(api.get_public_device_model_meanings())
    t = time.time() - t0
    print('%d device model meanings (%.2f s)' % (len(meanings), t))

    # Get a count of all public devices by meaning.
    counts = {}
    for device in devices:
        readings = device['model']['readings']
        for reading in readings:
            meaning = m = reading['meaning']
            counts[m] = counts[m] + 1 if counts.get(m, 0) else 1
    print('#public devices by meaning: %s' % json.dumps(counts, indent=4))


if __name__ == "__main__":
    print('Relayr API Pulse')
    show_versions()
    if not connected_to_internet():
        msg = 'Sorry, but you do not seem to have internet connectivity!'
        termcolor.cprint(msg, 'red')
        sys.exit(-1)    
    show_check()
