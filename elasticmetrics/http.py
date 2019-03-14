"""
elasticmetrics.http
~~~~~~~~~~~~~~~~~~~
common functionality over HTTP
"""
import ssl
import json
from logging import getLogger
from contextlib import closing
from base64 import b64encode
from .pystdlib.urllib_request import urlopen, Request
from .exceptions import ElasticMetricsError, ElasticMetricsRequestError


logger = getLogger(__name__)


class HttpClient(object):
    """Provides functionality to request URLs via HTTP/HTTPS,

    SSL settings for HTTPS calls can be tuned by passing an instance
    of ssl.SSLContext, or a dictionary with these keys:
        - no_cert_verify: skip certificate verification (insecure)
    (Python 2.7.9+)

    :param str host: server hostname/address
    :param int port: server port number
    :param str user: HTTP basic auth user
    :param str password: HTTP basic auth password
    :param str scheme: URL scheme, http/https
    :param dict headers: dictionary of additional headers
    :param ssl.SSLContext|dict ssl_context: an SSLContext instance, or dict for SSL config
    """

    default_port_http = 80
    default_port_https = 443

    def __init__(self, host, port=None, user='', password='', scheme='http', headers=None,
                 ssl_context=None):
        if scheme not in ('http', 'https'):
            raise ElasticMetricsError('invalid scheme "{}"'.format(scheme))

        self._host = host
        self._port = port or (self.default_port_https if scheme == 'https' else self.default_port_http)
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

        ssl_context = ssl_context or {}
        if scheme == 'https' and hasattr(ssl, 'create_default_context'):
            # Python < 2.7.9 doesn't support create_default_context, but also
            # urlopen wouldn't accept the context, so we won't use SSL context
            if isinstance(ssl_context, ssl.SSLContext):
                self._ssl_context = ssl_context
            else:
                self._ssl_context = ssl.create_default_context()
                if ssl_context.get('no_cert_verify'):
                    self._ssl_context.check_hostname = False
                    self._ssl_context.verify_mode = ssl.CERT_NONE
        else:
            self._ssl_context = None

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

    def _get_json(self, path):
        """Send a GET request to the URL path, expecting a JSON response.
        Returns the decoded data from response.

        :param str path: the URL path that responds with JSON
        :raise ElasticMetricsRequestError
        """
        request = self._create_request(path)
        url = request.get_full_url()
        try:
            logger.debug('requesting URL "{}"'.format(url))
            with closing(self._urlopen(request)) as response:
                logger.debug('URL "{}" response code "{}". decoding JSON'.format(url, response.getcode()))
                return json.loads(response.read().decode('utf-8'))
        except IOError as err:
            logger.error('failed to request URL "{}": {}'.format(url, err))
            raise ElasticMetricsRequestError('request error to URL "{}": {}'.format(url, err))
        except ValueError as err:
            logger.error('invalid JSON response from "{}": {}'.format(url, err))
            raise ElasticMetricsRequestError(
                      'invalid JSON response from "{}": {}'.format(url, err)
                  )

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
