"""
Compatibility helpers for Python 2 and 3.
"""

import sys


PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
PY26 = sys.version_info[:2] == (2, 6)

if PY2:
    from urllib import urlopen
    from urllib import urlencode
    from urllib2 import URLError
else:
    from urllib.request import urlopen
    from urllib.parse import urlencode
    from urllib.error import URLError
