#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Shows current Relayr API status on the command-line.

This script uses the Python bindings for the Relayr RESTful API as defined
in the ``relayr`` Python package. It should work as-is on Python 2 and 3.

Example:

$ python api_check.py 
Relayr API-Check
................................................................................
API: https://api.relayr.io
Python client version: 0.1.1
Python version: CPython 2.7.6
Date/Time: 2014-09-24T10:45:50.419279
................................................................................
server status ok: True (0.81 s)
140 publishers (0.35 s)
146 applications (0.44 s)
35 public devices (0.31 s)
6 device models (0.29 s)
8 device model meanings (0.31 s)
#public devices by meaning: {"acceleration": 7, "temperature": 9, \
"noise_level": 5, "angular_speed": 7, "color": 8, "luminosity": 8, \
"proximity": 8, "humidity": 9}

"""

import sys
import json
import time
import datetime
import platform
try:
    from urllib import urlopen
    from urllib2 import URLError
except ImportError:
    from urllib.request import urlopen
    from urllib.error import URLError

import termcolor

from relayr import core
from relayr.version import __version__ as relayr_version
from relayr.utils.terminalsize import get_terminal_size


def connected_to_internet():
    "Check if we have access to 'the internet', well some Google server."

    try:
        # Give IP address to avoid potential DNS issues.
        response=urlopen('http://74.125.228.100')
        return True
    except URLError as err:
        return False


def show_versions():
    "Show some versioning info."
    
    # Show header line.
    url = core.relayrAPI
    dt = datetime.datetime.now().isoformat()
    term_width = get_terminal_size()[0]
    print('.' * term_width)
    print('API: %s' % url)
    print('Python client version: %s' % relayr_version)
    pyimpl = platform.python_implementation()
    pyver = platform.python_version()
    print('Python version: %s %s' % (pyimpl, pyver))
    print('Date/Time: %s' % dt)
    print('.' * term_width)
    

def show_check():
    "Show some key numbers of the current state of the API."
    
    # Get number of all publishers (no credentials needed).
    t0 = time.time()
    try:
        # import pdb; pdb.set_trace();
        res = core.server_status()
        ok = res['database'] == 'ok'
    except:
        msg = 'Relayr API not reachable, sorry for that!'
        termcolor.cprint(msg, 'red')
        sys.exit(-1)
    t = time.time() - t0
    print('server status ok: %s (%.2f s)' % (ok, t))

    # Get number of all publishers (no credentials needed).
    t0 = time.time()
    publishers = core.list_all_publishers()
    t = time.time() - t0
    print('%d publishers (%.2f s)' % (len(publishers), t))

    # Get number of all apps (no credentials needed).
    t0 = time.time()
    apps = core.list_all_apps()
    t = time.time() - t0
    print('%d applications (%.2f s)' % (len(apps), t))
    
    # Get number of all public devices (no credentials needed).
    t0 = time.time()
    devices = core.list_all_public_devices()
    t = time.time() - t0
    print('%d public devices (%.2f s)' % (len(devices), t))

    # Get number of all device models (no credentials needed).
    t0 = time.time()
    models = core.list_all_device_models()
    t = time.time() - t0
    print('%d device models (%.2f s)' % (len(models), t))

    # Get number of all device model meanings (no credentials needed).
    t0 = time.time()
    meanings = core.list_all_device_model_meanings()
    t = time.time() - t0
    print('%d device model meanings (%.2f s)' % (len(meanings), t))

    # Get a count of all public devices by meaning (no credentials needed).
    devices = core.list_all_public_devices()
    counts = {}
    for device in devices:
        readings = device['model']['readings']
        for reading in readings:
            meaning = m = reading['meaning']
            counts[m] = counts[m] + 1 if counts.get(m, 0) else 1
    print('#public devices by meaning: %s' % json.dumps(counts))


if __name__ == "__main__":
    print('Relayr API-Check')
    show_versions()
    if not connected_to_internet():
        msg = 'Sorry, but you do not seem to have internet connectivity!'
        termcolor.cprint(msg, 'red')
        sys.exit(-1)    
    show_check()
