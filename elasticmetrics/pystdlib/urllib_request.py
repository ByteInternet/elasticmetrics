"""
elasticmetrics.pystdlib.urllib_request
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Proxy to Python standard library, abstracing 2/3 differences,
to keep try/imports in one place.
"""
try:
    from urllib2 import urlopen, Request
except ImportError:
    from urllib.request import urlopen, Request
