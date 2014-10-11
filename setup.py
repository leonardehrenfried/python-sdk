#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from os.path import join, dirname
from setuptools import setup

PY_VERSION = sys.version_info[0]

exec(open('relayr/version.py').read())

with open('README.rst') as f:
    long_description = f.read()

with open('requirements.txt') as f:
    install_requires = f.read().strip().split('\n')

# use external unittest for 2.6
if sys.version_info[:2] == (2, 6):
    install_requires.append('unittest2')

if PY_VERSION == 2:
    with open('requirements_py2.txt') as f:
        install_requires += f.read().strip().split('\n')

tests_require = [
    'requests>=1.0.0, <3.0.0',
]

setup(
    name = "relayr",
    description = "Python client for Relayr API",
    license="MIT",
    url = "https://github.com/relayr/python-sdk",
    long_description = long_description,
    version = __version__,
    author = "Relayr Team",
    author_email = "team@relayr.io",
    packages=['relayr', 'relayr.utils', 'relayr.tests'],
    # package_data={'relayr': ['docs/*']},
    keywords=['relayr', 'rest', 'api', 'python', 'client', 'iot', 'wunderbar'],
    classifiers = [
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Home Automation",
        "Topic :: Internet",
        "Topic :: System :: Distributed Computing",
        "Topic :: System :: Hardware",
        "Topic :: System :: Networking",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
    ],
    install_requires=install_requires,

    # test_suite='tests.test_api',
    tests_require=tests_require,
)
