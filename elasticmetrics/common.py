"""
elasticmetrics.common
~~~~~~~~~~~~~~~~~~~~~
common utilities
"""
import ssl
from base64 import b64encode
from .pystdlib.urllib_request import urlopen, Request
from .exceptions import ElasticMetricsError


class HttpClient(object):
    """Provides functionality to request URLs via HTTP/HTTPS,

    :param str host: server hostname/address
    :param int port: server port number
    :param str user: HTTP basic auth user
    :param str password: HTTP basic auth password
    :param str scheme: URL scheme, http/https
    :param dict headers: dictionary of additional headers
    """

    default_port = 80

    def __init__(self, host, port=None, user=None, password=None, scheme='http', headers=None):
        if scheme not in ('http', 'https'):
            raise ElasticMetricsError('invalid scheme "{}"'.format(scheme))

        self._host = host
        self._port = port or self.default_port
        self._user = user
        self._scheme = scheme
        self._password = password
        self._headers = headers or {}
        if user and password:
            # b64encode wants/returns bytes, we encode input and decode results
            basic_auth = b64encode(
                            u'{}:{}'.format(user, password).encode('utf-8')
                        ).decode('utf-8').strip()
            self._headers['Authorization'] = 'Basic {}'.format(basic_auth)

        # Python < 2.7.9 doesn't support create_default_context, but also
        # urlopen wouldn't accept the context, so no context is used
        if hasattr(ssl, 'create_default_context'):
            self._ssl_context = ssl.create_default_context() if scheme == 'https' else None
        else:
            self._ssl_context = None

    def ssl_no_cert_verify(self):
        """Disable SSL certificate verification.

        Note: This results to insecure connections, and better be avoided in production.
        This call mutates the client's SSLContext, and any request sent after
        calling this method, will be insecure.
        """
        if self._ssl_context:
            self._ssl_context.check_hostname = False
            self._ssl_context.verify_mode = ssl.CERT_NONE

    def _urlopen(self, request):
        """Send a request the response file like object (urllib2 style)
        :param urllib2.Request request: the request
        :return: response file like object
        """
        if self._ssl_context:
            return urlopen(request, context=self._ssl_context)
        return urlopen(request)

    def _create_request(self, path='/'):
        """Create a Request object from the specified URL path.
        :param str path: the URL path
        :return: Request
        """
        url = '{}://{}:{}/{}'.format(self._scheme, self._host, self._port, path)
        return Request(url, headers=self._headers)

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    @property
    def user(self):
        return self._user

    @property
    def password(self):
        return self._password

    @property
    def scheme(self):
        return self._scheme

    @property
    def headers(self):
        return self._headers.copy()

    @property
    def ssl_context(self):
        return self._ssl_context
